const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const { build } = require('esbuild');

const stubs = `
export const EthereumProvider = { init: () => testState.initWalletConnect() };
export const ethers = { providers: { Web3Provider: class {
    async listAccounts() { return ['0x123']; }
    async getNetwork() { return testState.network; }
    async lookupAddress() {
        testState.lookups++;
        if (testState.lookupError) throw new Error('RPC failed');
        return 'alice.eth';
    }
    getSigner() { return { signMessage: async () => 'signature' }; }
} } };
export const Mousetrap = { bind() {} };
export const QRCode = { toDataURL: async () => 'data:image/png;base64,test' };
export const SignatureType = { PERSONAL_SIGNATURE: 'Personal signature' };
export class SiweMessage {
    constructor(fields) { Object.assign(this, fields); }
    prepareMessage() { return 'message'; }
}
`;

const bundle = build({
    entryPoints: [path.join(__dirname, '../src/providers.js')],
    bundle: true,
    write: false,
    plugins: [{
        name: 'wallet-stubs',
        setup(builder) {
            builder.onResolve({ filter: /^(ethers|siwe|mousetrap|qrcode|@walletconnect\/ethereum-provider)$/ },
                (args) => ({ path: args.path, namespace: 'stub' }));
            builder.onLoad({ filter: /.*/, namespace: 'stub' }, (args) => ({
                contents: `${stubs}\n${args.path === 'mousetrap' ? 'export default Mousetrap;' : args.path === 'qrcode' ? 'export default QRCode;' : ''}`,
                loader: 'js',
            }));
        },
    }],
}).then((result) => result.outputFiles[0].text);

async function setup(network, { lookupError = false, restored = false, initWalletConnect } = {}) {
    const state = { network, lookupError, initWalletConnect, lookups: 0, errors: [], events: [] };
    const elements = new Map();
    const element = (id) => {
        if (!elements.has(id)) elements.set(id, {
            listeners: {},
            classList: { add() {}, remove() {}, toggle() {} },
            addEventListener(event, callback) { this.listeners[event] = callback; },
            removeEventListener(event, callback) {
                if (this.listeners[event] === callback) delete this.listeners[event];
            },
            setAttribute() {},
            removeAttribute() {},
            showModal() { this.open = true; },
            close() { this.open = false; },
        });
        return elements.get(id);
    };
    let ready;
    const document = {
        location: { host: 'example.com', origin: 'https://example.com' },
        body: { dataset: { walletconnectProjectId: 'test-project', walletconnectChainId: network.chainId } },
        getElementById: element,
        addEventListener(event, callback) { if (event === 'DOMContentLoaded') ready = callback; },
    };
    const window = {
        location: document.location,
        ethereum: { request: async () => {} },
        dispatchEvent(event) { state.events.push(event.type); },
    };
    const context = {
        document, window, testState: state, URL, Error,
        setTimeout(callback, delay) {
            state.startupTimeout = { callback, delay };
            return state.startupTimeout;
        },
        clearTimeout(timer) {
            if (state.startupTimeout === timer) delete state.startupTimeout;
        },
        Event: class { constructor(type) { this.type = type; } },
        console: { error: (...args) => state.errors.push(args) },
        localStorage: { setItem() {}, getItem() { return null; }, removeItem() {} },
        fetch: async (url, options) => {
            if (url === '/api/me') return restored
                ? { ok: true, json: async () => ({ address: '0x123' }) }
                : { status: 204 };
            if (url === '/api/nonce') return { ok: true, text: async () => 'nonce' };
            if (url === '/api/sign_in') {
                state.payload = JSON.parse(options.body);
                return { ok: true, json: async () => ({ address: '0x123' }) };
            }
            if (url === '/api/sign_out') return { ok: true };
            throw new Error(`Unexpected request: ${url}`);
        },
        alert(message) { throw new Error(message); },
    };
    vm.runInNewContext(await bundle, context);
    await ready();
    return { state, element };
}

async function login(network, lookupError = false) {
    const { state, element } = await setup(network, { lookupError });
    await element('metamask').listeners.click();
    return state;
}

test('notifies the terminal on sign-in, sign-out, and session restoration', async () => {
    const { state, element } = await setup({ chainId: 1 });
    assert.deepEqual(state.events, ['disconnectedState']);
    await element('metamask').listeners.click();
    assert.deepEqual(state.events, ['disconnectedState', 'connectedState']);
    await element('disconnectButton').listeners.click();
    assert.deepEqual(state.events, ['disconnectedState', 'connectedState', 'disconnectedState']);
    await element('metamask').listeners.click();
    assert.equal(state.events.at(-1), 'connectedState');

    const restored = await setup({ chainId: 1 }, { restored: true });
    assert.deepEqual(restored.state.events, ['connectedState']);
});

test('skips ENS lookup when the network has no ENS registry', async () => {
    const state = await login({ chainId: 11155111, name: 'unknown' });
    assert.equal(state.lookups, 0);
    assert.equal(state.errors.length, 0);
    assert.equal(state.payload.message.chainId, '11155111');
});

test('looks up ENS on supported networks and reports lookup failures', async () => {
    const network = { chainId: 1, ensAddress: 'registry' };
    const success = await login(network);
    assert.equal(success.lookups, 1);
    assert.equal(success.payload.ens, 'alice.eth');
    const failure = await login(network, true);
    assert.equal(failure.lookups, 1);
    assert.equal(failure.errors[0][0], 'ENS lookup failed:');
    assert.equal(failure.payload.message.chainId, '1');
});

test('shows progress immediately and reports a stalled relay without starting a late pairing', async () => {
    let finishInit;
    let connectCalls = 0;
    const { state, element } = await setup({ chainId: 1 }, {
        initWalletConnect: () => new Promise((resolve) => { finishInit = resolve; }),
    });
    const attempt = element('walletconnect').listeners.click();
    assert.equal(element('walletconnect-dialog').open, true);
    assert.match(element('walletconnect-progress').textContent, /Connecting/);
    assert.equal(element('walletconnect-pairing').hidden, true);
    assert.equal(state.startupTimeout.delay, 15000);
    state.startupTimeout.callback();
    await attempt;
    assert.equal(element('walletconnect-dialog').open, false);
    assert.match(element('walletconnect-error').textContent, /relay did not respond/);

    finishInit({ connect() { connectCalls++; } });
    await new Promise(setImmediate);
    assert.equal(connectCalls, 0);
});

test('displays the QR code, then allows silent cancellation and disconnects a late session', async () => {
    let onUri;
    let finishConnection;
    let disconnected = false;
    const topics = [];
    const provider = {
        on(event, callback) { onUri = callback; },
        removeListener() { onUri = undefined; },
        connect() { return new Promise((resolve) => { finishConnection = resolve; }); },
        async disconnect() { disconnected = true; },
        signer: { client: { core: { pairing: { async disconnect({ topic }) { topics.push(topic); } } } } },
    };
    const { state, element } = await setup({ chainId: 1 }, { initWalletConnect: async () => provider });
    const attempt = element('walletconnect').listeners.click();
    await new Promise(setImmediate);
    await onUri('wc:test-topic@2');
    assert.equal(element('walletconnect-pairing').hidden, false);
    assert.equal(element('walletconnect-uri').href, 'wc:test-topic@2');
    assert.equal(state.startupTimeout, undefined);
    element('walletconnect-close').listeners.click({ preventDefault() {} });
    await attempt;
    assert.equal(element('walletconnect-dialog').open, false);
    assert.equal(element('walletconnect-error').textContent, '');
    assert.deepEqual(topics, ['test-topic']);
    finishConnection();
    await new Promise(setImmediate);
    assert.equal(onUri, undefined);
    assert.equal(disconnected, true);
    assert.equal(state.payload, undefined);
});
