import React, { useRef, useEffect } from 'react';
import { View, Text, FlatList, StyleSheet, Image, ActivityIndicator } from 'react-native';
import Markdown from 'react-native-markdown-display';

const MessageBubble = ({ message }) => {
    const isUser = message.sender === 'user';

    return (
        <View style={[
            styles.bubbleContainer,
            isUser ? styles.userBubbleContainer : styles.botBubbleContainer
        ]}>
            {message.imageUri && (
                <Image source={{ uri: message.imageUri }} style={styles.messageImage} />
            )}
            <View style={[
                styles.bubble,
                isUser ? styles.userBubble : styles.botBubble
            ]}>
                {isUser ? (
                    <Text style={styles.userText}>{message.text}</Text>
                ) : (
                    <Markdown style={markdownStyles}>
                        {message.text}
                    </Markdown>
                )}
            </View>
        </View>
    );
};

const ChatInterface = ({ messages, isTyping }) => {
    const flatListRef = useRef();

    useEffect(() => {
        if (messages.length > 0) {
            flatListRef.current?.scrollToEnd({ animated: true });
        }
    }, [messages]);

    return (
        <View style={styles.container}>
            <FlatList
                ref={flatListRef}
                data={messages}
                keyExtractor={(item) => item.id}
                renderItem={({ item }) => <MessageBubble message={item} />}
                contentContainerStyle={styles.listContent}
                ListFooterComponent={
                    isTyping && (
                        <View style={styles.typingContainer}>
                            <ActivityIndicator size="small" color="#4a90e2" />
                            <Text style={styles.typingText}>Doctor is thinking...</Text>
                        </View>
                    )
                }
            />
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f5f7fb',
    },
    listContent: {
        padding: 15,
        paddingBottom: 20,
    },
    bubbleContainer: {
        marginBottom: 15,
        maxWidth: '85%',
    },
    userBubbleContainer: {
        alignSelf: 'flex-end',
        alignItems: 'flex-end',
    },
    botBubbleContainer: {
        alignSelf: 'flex-start',
        alignItems: 'flex-start',
    },
    bubble: {
        padding: 12,
        borderRadius: 18,
    },
    userBubble: {
        backgroundColor: '#4a90e2',
        borderBottomRightRadius: 4,
    },
    botBubble: {
        backgroundColor: '#ffffff',
        borderBottomLeftRadius: 4,
        borderWidth: 1,
        borderColor: '#e1e4e8',
    },
    userText: {
        color: '#ffffff',
        fontSize: 16,
    },
    messageImage: {
        width: 200,
        height: 200,
        borderRadius: 12,
        marginBottom: 5,
    },
    typingContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginLeft: 10,
        marginBottom: 10,
    },
    typingText: {
        marginLeft: 8,
        color: '#666',
        fontSize: 14,
    },
});

const markdownStyles = {
    body: {
        fontSize: 16,
        color: '#333',
    },
    paragraph: {
        marginBottom: 10,
    },
};

export default ChatInterface;
