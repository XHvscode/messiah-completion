# -*- coding:utf-8 -*-

from pygls.lsp.methods import (COMPLETION, DEFINITION, TEXT_DOCUMENT_DID_CHANGE,
                               TEXT_DOCUMENT_DID_CLOSE, TEXT_DOCUMENT_DID_OPEN, TEXT_DOCUMENT_DID_SAVE,
                               TEXT_DOCUMENT_SEMANTIC_TOKENS_FULL, WORKSPACE_DID_CHANGE_WATCHED_FILES)

from pygls.lsp.types import (List, Union,
                             CompletionItem, CompletionList, CompletionOptions, CompletionItemKind,
                             DefinitionParams,
                             CompletionParams, ConfigurationItem,
                             ConfigurationParams, Diagnostic,
                             DidChangeTextDocumentParams,
                             DidCloseTextDocumentParams,
                             DidSaveTextDocumentParams,
                             DidOpenTextDocumentParams,
                             DidChangeWatchedFilesParams,
                             MessageType, Position, Location, LocationLink,
                             Range, Registration, RegistrationParams,
                             SemanticTokens, SemanticTokensLegend, SemanticTokensParams,
                             Unregistration, UnregistrationParams)

from pygls.lsp.types.basic_structures import (WorkDoneProgressBegin,
                                              WorkDoneProgressEnd,
                                              WorkDoneProgressReport)

from pygls.uris import from_fs_path, to_fs_path
