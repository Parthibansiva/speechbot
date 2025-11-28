import React, { useState } from 'react';
import { StyleSheet, SafeAreaView, View, StatusBar, Platform, Alert, Modal, Text, TouchableOpacity, FlatList } from 'react-native';
import { Audio } from 'expo-av';
import { Ionicons } from '@expo/vector-icons';
import ChatInterface from './components/ChatInterface';
import InputArea from './components/InputArea';
import { sendChat } from './services/api';

const LANGUAGES = [
  { id: 'en', name: 'English' },
  { id: 'ta', name: 'Tamil' },
  { id: 'hi', name: 'Hindi' },
  { id: 'te', name: 'Telugu' },
  { id: 'kn', name: 'Kannada' },
  { id: 'ml', name: 'Malayalam' },
  { id: 'bn', name: 'Bengali' },
  { id: 'gu', name: 'Gujarati' },
  { id: 'mr', name: 'Marathi' },
  { id: 'pa', name: 'Punjabi' },
];

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      text: 'Hello! I am your AI Doctor. You can show me images, speak to me, or type your symptoms.',
      sender: 'bot',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [language, setLanguage] = useState('English');
  const [modalVisible, setModalVisible] = useState(false);

  const handleSend = async ({ text, audioUri, imageUri }) => {
    // Add user message immediately
    const userMessage = {
      id: Date.now().toString(),
      text: text || (audioUri ? '🎤 Audio Message' : '📷 Image Message'),
      sender: 'user',
      imageUri: imageUri,
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Prepare history for backend (exclude current message, filter for role/content)
      const history = messages
        .filter(msg => msg.id !== 'welcome') // Exclude welcome message if it's not a real turn
        .map(msg => ({
          role: msg.sender === 'user' ? 'user' : 'assistant',
          content: msg.text
        }));

      const response = await sendChat(text, audioUri, imageUri, history, language);

      // Add bot response
      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: response.response,
        sender: 'bot',
      };
      setMessages(prev => [...prev, botMessage]);

      // Play audio if available
      if (response.audio_base64) {
        playAudio(response.audio_base64);
      }

    } catch (error) {
      Alert.alert("Error", "Failed to get response from the doctor.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  const playAudio = async (base64Audio) => {
    try {
      const soundObject = new Audio.Sound();
      await soundObject.loadAsync({ uri: `data:audio/mp3;base64,${base64Audio}` });
      await soundObject.playAsync();
    } catch (error) {
      console.error("Failed to play audio", error);
    }
  };

  const renderLanguageItem = ({ item }) => (
    <TouchableOpacity
      style={styles.languageItem}
      onPress={() => {
        setLanguage(item.name);
        setModalVisible(false);
      }}
    >
      <Text style={[styles.languageText, language === item.name && styles.selectedLanguageText]}>
        {item.name}
      </Text>
      {language === item.name && <Ionicons name="checkmark" size={20} color="#4a90e2" />}
    </TouchableOpacity>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />

      {/* Header with Language Selector */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Doctor</Text>
        <TouchableOpacity onPress={() => setModalVisible(true)} style={styles.langButton}>
          <Ionicons name="language" size={20} color="#4a90e2" />
          <Text style={styles.langButtonText}>{language}</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        <ChatInterface messages={messages} isTyping={isLoading} />
        <InputArea onSend={handleSend} isLoading={isLoading} />
      </View>

      {/* Language Selection Modal */}
      <Modal
        animationType="slide"
        transparent={true}
        visible={modalVisible}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Select Language</Text>
              <TouchableOpacity onPress={() => setModalVisible(false)}>
                <Ionicons name="close" size={24} color="#333" />
              </TouchableOpacity>
            </View>
            <FlatList
              data={LANGUAGES}
              renderItem={renderLanguageItem}
              keyExtractor={item => item.id}
            />
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: Platform.OS === 'android' ? StatusBar.currentHeight : 0,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 15,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    backgroundColor: '#fff',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  langButton: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 8,
    backgroundColor: '#f0f2f5',
    borderRadius: 20,
  },
  langButtonText: {
    marginLeft: 5,
    color: '#4a90e2',
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    maxHeight: '50%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 15,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
  },
  languageItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  languageText: {
    fontSize: 16,
    color: '#333',
  },
  selectedLanguageText: {
    color: '#4a90e2',
    fontWeight: 'bold',
  },
});
