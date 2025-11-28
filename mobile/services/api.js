import { Platform } from 'react-native';

// Replace with your machine's IP address if testing on physical device
// For Android Emulator, use 'http://10.0.2.2:8000'
// For iOS Simulator, use 'http://localhost:8000'
// const BASE_URL = Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://localhost:8000';
const BASE_URL = 'http://10.76.78.249:8000'; // Using local IP for broader compatibility

export const sendChat = async (text, audioUri, imageUri, history = [], language = 'English') => {
    const formData = new FormData();

    if (text) {
        formData.append('text', text);
    }

    if (history.length > 0) {
        formData.append('history', JSON.stringify(history));
    }

    if (language) {
        formData.append('language', language);
    }

    if (audioUri) {
        const uriParts = audioUri.split('.');
        const fileType = uriParts[uriParts.length - 1];
        if (Platform.OS === 'web') {
            const response = await fetch(audioUri);
            const blob = await response.blob();
            formData.append('audio', blob, `recording.${fileType}`);
        } else {
            formData.append('audio', {
                uri: audioUri,
                name: `recording.${fileType}`,
                type: `audio/${fileType}`,
            });
        }
    }

    if (imageUri) {
        const uriParts = imageUri.split('.');
        const fileType = uriParts[uriParts.length - 1] || 'jpg'; // Default to jpg if no extension
        if (Platform.OS === 'web') {
            const response = await fetch(imageUri);
            const blob = await response.blob();
            formData.append('image', blob, `image.${fileType}`);
        } else {
            formData.append('image', {
                uri: imageUri,
                name: `image.${fileType}`,
                type: `image/${fileType}`,
            });
        }
    }

    try {
        const response = await fetch(`${BASE_URL}/chat`, {
            method: 'POST',
            body: formData,
            headers: {
                // 'Content-Type': 'multipart/form-data', // Let the browser set this with the boundary
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`API Error: ${response.status} - ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('API Request Failed:', error);
        throw error;
    }
};
