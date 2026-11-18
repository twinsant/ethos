import { EthereumProvider } from '@walletconnect/ethereum-provider';
import { ethers } from 'ethers';
import Mousetrap from 'mousetrap';
import QRCode from 'qrcode';
import { SignatureType, SiweMessage } from 'siwe';

let walletconnect;
let walletConnectInitialization;
let walletConnectPairingPending = false;
let signingIn = false;
const walletProviderKey = 'ethos-wallet-provider';
const walletConnectCancelled = new Error('WalletConnect connection cancelled.');

const element = (id) => document.getElementById(id);
const updateTitle = (text) => { element('title').innerText = text; };

function blockSave() {
    element('saveButton').removeEventListener('click', save);
    element('saveButton').setAttribute('disabled', 'true');
    element('unsaved').innerText = '';
    window.onbeforeunload = null;
}

function enableSave() {
    element('saveButton').addEventListener('click', save);
    element('saveButton').removeAttribute('disabled');
    element('unsaved').innerText = '- (***Unsaved Changes***)';
    window.onbeforeunload = () => '(***Unsaved Changes***)';
}

async function save(event) {
    event?.preventDefault();
    const text = element('notepad').value;
    if (new TextEncoder().encode(JSON.stringify({ text })).length > 43610) {
        alert('Your message is too big.');
        return;
    }
    const response = await fetch('/api/save', {
        method: 'PUT',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
    });
    if (!response.ok) throw new Error('Unable to save the note.');
    blockSave();
}

function connectedState(text, address, ens) {
    element('metamask').classList.add('hidden');
    element('walletconnect').classList.add('hidden');
    element('closeButton').addEventListener('click', signOut);
    element('closeButton').removeAttribute('disabled');
    element('saveButton').classList.remove('hidden');
    element('disconnectButton').classList.remove('hidden');
    if (text) element('notepad').value = text;
    blockSave();
    updateTitle(ens ?? address);
    window.dispatchEvent(new Event('connectedState'));
}

function disconnectedState() {
    element('metamask').classList.toggle('hidden', !window.ethereum);
    element('walletconnect').classList.remove('hidden');
    element('closeButton').removeEventListener('click', signOut);
    element('closeButton').setAttribute('disabled', 'disabled');
    element('saveButton').classList.add('hidden');
    element('disconnectButton').classList.add('hidden');
    window.dispatchEvent(new Event('disconnectedState'));
}

async function initializeWalletConnect() {
    const projectId = document.body.dataset.walletconnectProjectId;
    const chainId = Number(document.body.dataset.walletconnectChainId);
    if (!projectId || !Number.isSafeInteger(chainId) || chainId < 1) {
        throw new Error('WalletConnect is not configured. Contact the site administrator.');
    }

    walletConnectInitialization ??= EthereumProvider.init({
        projectId,
        optionalChains: [chainId],
        showQrModal: false,
        metadata: {
            name: 'EthOS',
            description: 'EthOS',
            url: window.location.origin,
            icons: [new URL('/static/img/favicon.png', window.location.origin).href],
        },
    }).catch((error) => {
        walletConnectInitialization = undefined;
        throw error;
    });
    return walletConnectInitialization;
}

async function connectWalletConnect() {
    if (walletConnectPairingPending) {
        throw new Error('The previous WalletConnect attempt is still closing. Wait a moment or reload the page.');
    }
    const dialog = element('walletconnect-dialog');
    const progress = element('walletconnect-progress');
    const pairing = element('walletconnect-pairing');
    progress.textContent = 'Connecting to the WalletConnect relay…';
    pairing.hidden = true;
    dialog.showModal();
    let provider;
    let cancelled = false;
    let completed = false;
    let pairingTopic;
    const disconnectPairing = () => {
        if (pairingTopic) {
            provider.signer.client.core.pairing.disconnect({ topic: pairingTopic })
                .catch((error) => console.error('WalletConnect pairing cleanup failed:', error));
        }
    };
    let cancelConnection;
    let stopConnection;
    const cancellation = new Promise((_, reject) => {
        stopConnection = (error) => {
            if (completed || cancelled) return;
            cancelled = true;
            disconnectPairing();
            reject(error);
        };
        cancelConnection = (event) => {
            event.preventDefault();
            stopConnection(walletConnectCancelled);
        };
    });
    dialog.addEventListener('cancel', cancelConnection);
    element('walletconnect-close').addEventListener('click', cancelConnection);
    const startupTimeout = setTimeout(() => {
        stopConnection(new Error('WalletConnect relay did not respond. Check your network and try again, or use MetaMask.'));
    }, 15000);
    const displayUri = async (uri) => {
        try {
            const match = /^wc:([^@]+)@2(?:\?|$)/.exec(uri);
            if (!match) throw new Error('Invalid WalletConnect pairing URI.');
            pairingTopic = match[1];
            if (cancelled) {
                disconnectPairing();
                return;
            }
            const qr = await QRCode.toDataURL(uri, { width: 280, margin: 2 });
            if (cancelled || completed) return;
            element('walletconnect-qr').src = qr;
            element('walletconnect-uri').href = uri;
            pairing.hidden = false;
            progress.textContent = 'Scan with your wallet, or open the link on your phone.';
            clearTimeout(startupTimeout);
        } catch (error) {
            stopConnection(error);
        }
    };
    const connection = (async () => {
        provider = await initializeWalletConnect();
        if (cancelled) return;
        provider.on('display_uri', displayUri);
        walletConnectPairingPending = true;
        try {
            await provider.connect();
            if (cancelled) await provider.disconnect();
        } finally {
            walletConnectPairingPending = false;
            provider.removeListener('display_uri', displayUri);
        }
    })();
    connection.catch((error) => {
        if (cancelled) console.error('WalletConnect attempt ended after cancellation:', error);
    });
    try {
        await Promise.race([connection, cancellation]);
        completed = true;
        return provider;
    } finally {
        clearTimeout(startupTimeout);
        dialog.removeEventListener('cancel', cancelConnection);
        element('walletconnect-close').removeEventListener('click', cancelConnection);
        if (dialog.open) dialog.close();
    }
}

async function signIn(connector) {
    if (signingIn) return;
    signingIn = true;
    const walletError = element('walletconnect-error');
    walletError.textContent = '';
    try {
        let wallet;
        if (connector === 'metamask') {
            if (!window.ethereum) throw new Error('MetaMask is not available.');
            await window.ethereum.request({ method: 'eth_requestAccounts' });
            wallet = window.ethereum;
        } else {
            walletconnect = await connectWalletConnect();
            wallet = walletconnect;
        }

        const provider = new ethers.providers.Web3Provider(wallet);
        const [address] = await provider.listAccounts();
        if (!address) throw new Error('Address not found.');
        const network = await provider.getNetwork();
        let ens;
        if (network.ensAddress) {
            try {
                ens = await provider.lookupAddress(address);
            } catch (error) {
                console.error('ENS lookup failed:', error);
            }
        }
        const nonceResponse = await fetch('/api/nonce', { credentials: 'include' });
        if (!nonceResponse.ok) throw new Error('Unable to obtain a sign-in nonce.');
        const message = new SiweMessage({
            domain: document.location.host,
            address,
            chainId: `${network.chainId}`,
            uri: document.location.origin,
            version: '1',
            statement: 'EthOS',
            type: SignatureType.PERSONAL_SIGNATURE,
            nonce: await nonceResponse.text(),
        });
        message.signature = await provider.getSigner().signMessage(message.prepareMessage());
        const response = await fetch('/api/sign_in', {
            method: 'POST',
            body: JSON.stringify({ message, ens }),
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
        });
        if (!response.ok) throw new Error('Sign-in failed. Check your wallet account and network.');
        const user = await response.json();
        connectedState(user.text, user.address, user.ens);
        try {
            localStorage.setItem(walletProviderKey, connector);
        } catch (error) {
            console.error('Unable to remember the wallet provider:', error);
            alert('Signed in, but wallet disconnection after a reload may not work.');
        }
    } catch (error) {
        if (error === walletConnectCancelled) return;
        if (connector === 'walletconnect' && walletconnect?.session) {
            try {
                await walletconnect.disconnect();
                walletconnect = undefined;
            } catch (disconnectError) {
                console.error('WalletConnect disconnect failed:', disconnectError);
            }
        }
        console.error('Sign-in failed:', error);
        const message = error instanceof Error ? error.message : 'Sign-in failed.';
        if (connector === 'walletconnect') walletError.textContent = message;
        else alert(message);
    } finally {
        signingIn = false;
    }
}

async function signOut() {
    try {
        const response = await fetch('/api/sign_out', { method: 'POST', credentials: 'include' });
        if (!response.ok) throw new Error('Unable to sign out.');
        updateTitle('Untitled');
        element('notepad').value = '';
        disconnectedState();
        if (!walletconnect && localStorage.getItem(walletProviderKey) === 'walletconnect') {
            walletconnect = await initializeWalletConnect();
        }
        if (walletconnect?.session) await walletconnect.disconnect();
        walletconnect = undefined;
        localStorage.removeItem(walletProviderKey);
    } catch (error) {
        console.error('Sign-out failed:', error);
        alert(error instanceof Error ? error.message : 'Sign-out failed.');
    }
}

function maximize() {
    const button = element('toggleSize');
    const notepad = element('notepad');
    const maximized = button.ariaLabel === 'Restore';
    button.ariaLabel = maximized ? 'Maximize' : 'Restore';
    notepad.style.width = maximized ? '460px' : '99.7vw';
    notepad.style.height = maximized ? '320px' : '91.7vh';
}

document.addEventListener('DOMContentLoaded', async () => {
    element('toggleSize')?.addEventListener('click', maximize);
    element('disconnectButton').addEventListener('click', signOut);
    element('metamask').addEventListener('click', () => signIn('metamask'));
    element('walletconnect').addEventListener('click', () => signIn('walletconnect'));
    element('saveButton').addEventListener('click', save);
    element('notepad').addEventListener('input', enableSave);
    Mousetrap.bind('mod+s', save);
    try {
        const response = await fetch('/api/me', { credentials: 'include' });
        if (response.status === 204) disconnectedState();
        else if (response.ok) {
            const user = await response.json();
            connectedState(user.text, user.address, user.ens);
        } else throw new Error('Unable to check the current session.');
    } catch (error) {
        console.error('Session check failed:', error);
        alert('Unable to check the current session.');
    }
});
