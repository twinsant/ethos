const assert = require('node:assert/strict');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');
const { build } = require('esbuild');

const stubs = `
export const EthereumProvider = {};
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
export const QRCode = {};
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

async function login(network, lookupError = false) {
    const state = { network, lookupError, lookups: 0, errors: [] };
    const elements = new Map();
    const element = (id) => {
        if (!elements.has(id)) elements.set(id, {
            listeners: {},
            classList: { add() {}, remove() {}, toggle() {} },
            addEventListener(event, callback) { this.listeners[event] = callback; },
            removeEventListener() {},
            setAttribute() {},
            removeAttribute() {},
        });
        return elements.get(id);
    };
    let ready;
    const document = {
        location: { host: 'example.com', origin: 'https://example.com' },
        getElementById: element,
        addEventListener(event, callback) { if (event === 'DOMContentLoaded') ready = callback; },
    };
    const window = { ethereum: { request: async () => {} } };
    const context = {
        document, window, testState: state,
        console: { error: (...args) => state.errors.push(args) },
        localStorage: { setItem() {} },
        fetch: async (url, options) => {
            if (url === '/api/me') return { status: 204 };
            if (url === '/api/nonce') return { ok: true, text: async () => 'nonce' };
            if (url === '/api/sign_in') {
                state.payload = JSON.parse(options.body);
                return { ok: true, json: async () => ({ address: '0x123' }) };
            }
            throw new Error(`Unexpected request: ${url}`);
        },
        alert(message) { throw new Error(message); },
    };
    vm.runInNewContext(await bundle, context);
    await ready();
    await element('metamask').listeners.click();
    return state;
}

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
