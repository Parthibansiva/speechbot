import React, { useState, useEffect } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, ActivityIndicator, Text, Image, Alert } from 'react-native';
import { Ionicons, MaterialIcons, MaterialCommunityIcons } from '@expo/vector-icons';
import { Audio } from 'expo-av';
import * as ImagePicker from 'expo-image-picker';

const InputArea = ({ onSend, isLoading }) => {
    const [text, setText] = useState('');
    const [recording, setRecording] = useState(null);
    const [isRecording, setIsRecording] = useState(false);
    const [isRespirationRecording, setIsRespirationRecording] = useState(false);
    const [selectedImage, setSelectedImage] = useState(null);

    useEffect(() => {
        (async () => {
            await Audio.requestPermissionsAsync();
            await ImagePicker.requestMediaLibraryPermissionsAsync();
            await ImagePicker.requestCameraPermissionsAsync();
        })();
    }, []);

    const startRecording = async () => {
        try {
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            setRecording(recording);
            setIsRecording(true);
        } catch (err) {
            console.error('Failed to start recording', err);
        }
    };

    const stopRecording = async () => {
        if (!recording) return;
        setIsRecording(false);
        await recording.stopAndUnloadAsync();
        const uri = recording.getURI();
        setRecording(null);
        onSend({ audioUri: uri });
    };

    const startRespirationRecording = async () => {
        try {
            await Audio.setAudioModeAsync({
                allowsRecordingIOS: true,
                playsInSilentModeIOS: true,
            });

            const { recording } = await Audio.Recording.createAsync(
                Audio.RecordingOptionsPresets.HIGH_QUALITY
            );
            
            setIsRespirationRecording(true);
            
            // Record for exactly 6 seconds as required by the model
            setTimeout(async () => {
                await recording.stopAndUnloadAsync();
                const uri = recording.getURI();
                setIsRespirationRecording(false);
                onSend({ audioUri: uri, type: 'respiration' });
            }, 6000);

        } catch (err) {
            console.error('Failed to start respiration recording', err);
            setIsRespirationRecording(false);
        }
    };

    const pickImage = async () => {
        let result = await ImagePicker.launchImageLibraryAsync({
            mediaTypes: ImagePicker.MediaTypeOptions.Images,
            allowsEditing: true,
            aspect: [4, 3],
            quality: 1,
        });

        if (!result.canceled) {
            setSelectedImage(result.assets[0].uri);
        }
    };

    const takePhoto = async () => {
        let result = await ImagePicker.launchCameraAsync({
            allowsEditing: true,
            aspect: [4, 3],
            quality: 1,
        });

        if (!result.canceled) {
            setSelectedImage(result.assets[0].uri);
        }
    };

    const handleSend = () => {
        if (text.trim() || selectedImage) {
            onSend({ text, imageUri: selectedImage });
            setText('');
            setSelectedImage(null);
        }
    };

    return (
        <View style={styles.container}>
            {selectedImage && (
                <View style={styles.imagePreview}>
                    <Image source={{ uri: selectedImage }} style={styles.previewImage} />
                    <TouchableOpacity
                        style={styles.removeImage}
                        onPress={() => setSelectedImage(null)}
                    >
                        <Ionicons name="close-circle" size={24} color="white" />
                    </TouchableOpacity>
                </View>
            )}

            {isRespirationRecording && (
                <View style={styles.respirationOverlay}>
                    <ActivityIndicator color="#4a90e2" />
                    <Text style={styles.respirationText}>Recording Respiration (6s)... Keep breathing naturally.</Text>
                </View>
            )}

            <View style={styles.inputContainer}>
                <TouchableOpacity onPress={pickImage} style={styles.iconButton}>
                    <Ionicons name="image-outline" size={24} color="#4a90e2" />
                </TouchableOpacity>

                <TouchableOpacity onPress={takePhoto} style={styles.iconButton}>
                    <Ionicons name="camera-outline" size={24} color="#4a90e2" />
                </TouchableOpacity>

                <TouchableOpacity 
                    onPress={startRespirationRecording} 
                    style={styles.iconButton}
                    disabled={isRespirationRecording || isRecording || isLoading}
                >
                    <MaterialCommunityIcons 
                        name="lungs" 
                        size={24} 
                        color={isRespirationRecording ? "#e74c3c" : "#4a90e2"} 
                    />
                </TouchableOpacity>

                <TextInput
                    style={styles.input}
                    placeholder="Message..."
                    value={text}
                    onChangeText={setText}
                    multiline
                    editable={!isRespirationRecording}
                />

                {text.trim() || selectedImage ? (
                    <TouchableOpacity onPress={handleSend} style={styles.sendButton} disabled={isLoading || isRespirationRecording}>
                        {isLoading ? (
                            <ActivityIndicator color="white" size="small" />
                        ) : (
                            <Ionicons name="send" size={20} color="white" />
                        )}
                    </TouchableOpacity>
                ) : (
                    <TouchableOpacity
                        onPress={isRecording ? stopRecording : startRecording}
                        style={[styles.micButton, isRecording && styles.recordingButton]}
                        disabled={isRespirationRecording || isLoading}
                    >
                        <MaterialIcons name={isRecording ? "stop" : "mic"} size={24} color="white" />
                    </TouchableOpacity>
                )}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        padding: 10,
        backgroundColor: '#fff',
        borderTopWidth: 1,
        borderTopColor: '#eee',
    },
    imagePreview: {
        marginBottom: 10,
        position: 'relative',
        alignSelf: 'flex-start',
    },
    previewImage: {
        width: 100,
        height: 100,
        borderRadius: 10,
    },
    removeImage: {
        position: 'absolute',
        top: -5,
        right: -5,
        backgroundColor: 'rgba(0,0,0,0.5)',
        borderRadius: 12,
    },
    respirationOverlay: {
        flexDirection: 'row',
        alignItems: 'center',
        padding: 10,
        backgroundColor: '#f0f2f5',
        borderRadius: 10,
        marginBottom: 10,
    },
    respirationText: {
        marginLeft: 10,
        color: '#4a90e2',
        fontSize: 12,
        fontWeight: 'bold',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        backgroundColor: '#f0f2f5',
        borderRadius: 25,
        paddingHorizontal: 10,
        paddingVertical: 5,
    },
    input: {
        flex: 1,
        maxHeight: 100,
        paddingHorizontal: 10,
        fontSize: 16,
        color: '#333',
    },
    iconButton: {
        padding: 8,
    },
    sendButton: {
        backgroundColor: '#4a90e2',
        width: 40,
        height: 40,
        borderRadius: 20,
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: 5,
    },
    micButton: {
        backgroundColor: '#4a90e2',
        width: 40,
        height: 40,
        borderRadius: 20,
        justifyContent: 'center',
        alignItems: 'center',
        marginLeft: 5,
    },
    recordingButton: {
        backgroundColor: '#e74c3c',
    },
});

export default InputArea;
