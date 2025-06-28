// This file defines the JavaScript object structures that mirror the Pydantic models
// used in the backend for WebSocket communication.

// Base WebSocket Message Structure
export const WebSocketMessage = {
    type: 'string', // e.g., "auth_request", "chat_request", "image_upload_request", "auth_response", "chat_response", "image_upload_response", "error"
    payload: 'object' // The specific payload depends on the message type
};

// --- Authentication Payloads ---
export const AuthRequestPayload = {
    action: 'string', // "register" or "login"
    identifier: 'string', // For login: user ID or username
    username: 'string',   // For register
    password: 'string',
    id: 'string',         // For register: user ID
    role: 'string'        // For register: "student", "teacher", "admin"
};

export const AuthResponsePayload = {
    status: 'string', // "success" or "error"
    message: 'string',
    token: 'string | null',
    user_id: 'string | null',
    username: 'string | null',
    role: 'string | null'
};

// --- Chat Payloads ---
export const ChatMessage = {
    role: 'string', // "user" or "assistant"
    content: 'object' // e.g., { text: "..." }
};

export const ChatRequestPayload = {
    history: 'array', // Array of ChatMessage
    current_text: 'string',
    current_image_paths: 'array' // Array of strings (image URLs)
};

export const ChatResponseContent = {
    data: 'string | null',    // For "text" type
    status: 'string | null',  // For "agent_status" type
    message: 'string | null', // For "agent_status" type
    reason: 'string | null'   // For "stop" type
};

export const ChatResponsePayload = {
    type: 'string', // "text", "agent_status", "stop"
    content: 'object' // ChatResponseContent
};

// --- Image Upload Payloads ---
export const ImageUploadRequestPayload = {
    filename: 'string',
    image_data: 'string' // Base64 encoded image data
};

export const ImageUploadResponsePayload = {
    status: 'string',
    message: 'string',
    image_path: 'string | null'
};

// --- Error Payload ---
export const ErrorPayload = {
    message: 'string'
};