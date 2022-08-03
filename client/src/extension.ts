/* --------------------------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * Licensed under the MIT License. See License.txt in the project root for license information.
 * ------------------------------------------------------------------------------------------ */

import * as net from "net";
import * as path from 'path';
import { workspace, ExtensionContext, ExtensionMode } from 'vscode';

import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;




export function activate(context: ExtensionContext) {

    // Options to control the language client
    const clientOptions: LanguageClientOptions = {
        // Register the server for plain text documents
        documentSelector: [{ scheme: 'file', language: 'python' }],
        outputChannelName: "[pygls] PythonLanguageServer",
        synchronize: {
            // Notify the server about file changes to '.clientrc files contained in the workspace
            fileEvents: workspace.createFileSystemWatcher('**/class_relation.json')
        }
    };


    if (context.extensionMode === ExtensionMode.Development) {
        // Create the language client and start the client.

        const serverOptions: ServerOptions = () => {
            return new Promise((resolve /*, reject */) => {
                const clientSocket = new net.Socket();
                clientSocket.connect(16471, "127.0.0.1", () => {
                    resolve({
                        reader: clientSocket,
                        writer: clientSocket,
                    });
                });
            });
        };

        client = new LanguageClient(
            'languageServerExample',
            'Language Server Example',
            serverOptions,
            clientOptions
        );

    } else {

        function startLangServer(
            command: string,
            args: string[],
            cwd: string
        ): LanguageClient {
            const serverOptions: ServerOptions = {
                args,
                command,
                options: { cwd },
            };

            return new LanguageClient(command, serverOptions, clientOptions);
        }
        const cwd = path.join(__dirname, "..", "..");

        client = startLangServer("server/main.xh", [], cwd);
    }

    // Start the client. This will also launch the server
    // client.start();
    const disposable = client.start();
    context.subscriptions.push(disposable);
    client.onReady().then(() => {
        console.log('lsp-messiah server is ready');
    });
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
