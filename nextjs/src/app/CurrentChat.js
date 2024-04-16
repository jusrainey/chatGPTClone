import { useState, useEffect } from 'react';
import styles from './CurrentChat.module.css';
import { fetchSessions } from './ChatHistory'
export default function CurrentChat({ activeSession }) {

    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [eventSource, setEventSource] = useState(null);  // State to manage EventSource


    useEffect(() => {
    setMessages([]);  // Clear messages when the session changes
    // Optionally, load chat history for the new session
    loadChatHistory(activeSession.id);
}, [activeSession]);

const loadChatHistory = async (sessionId) => {
    const historyUrl = `http://127.0.0.1:5000/get_history/${sessionId}`;
    try {
        const response = await fetch(historyUrl);
        if (!response.ok) throw new Error('Failed to fetch history');
        const historyData = await response.json();
        const formattedMessages = historyData.map(msg => [
            { from: 'user', text: msg.user_input },
            { from: 'bot', text: msg.bot_response }
        ]).flat();
        setMessages(formattedMessages);
    } catch (error) {
        console.error("Error fetching chat history:", error);
    }
};



    const sendMessage = () => {


        if (!input.trim()) return;

        const queryParams = new URLSearchParams({
            session_id: activeSession.id,
            user_input: input
        }).toString();

        const eventSource = new EventSource(`http://127.0.0.1:5000/get_response?${queryParams}`);
            setEventSource(eventSource); // Update the state to the new EventSource instance


        let fullResponse = '';  // Initialize empty string to accumulate response

        eventSource.onmessage = function(event) {
            const newMessage = JSON.parse(event.data);
            if (newMessage.bot_response) {
                fullResponse += newMessage.bot_response;  // Accumulate the response
                setMessages(prev => [...prev.slice(0, -1), { from: 'bot', text: fullResponse }]);
            }
        };

        setMessages(prev => [...prev, { from: 'user', text: input }, { from: 'bot', text: '' }]);  // Add user input and initial bot response

        eventSource.onerror = function() {
            eventSource.close();
            console.log("EventSource failed.");
            saveChatToDatabase(activeSession.id, input, fullResponse);  // Save chat after receiving full response

        };

        setInput(''); // Clear input after sending
    };
    const saveChatToDatabase = async (sessionId, userInput, botResponse) => {
        try {
            const response = await fetch('http://127.0.0.1:5000/save_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    user_input: userInput,
                    bot_response: botResponse
                }),
            });
            if (!response.ok) throw new Error('Failed to save chat');
            console.log('Chat saved successfully');
        } catch (error) {
            console.error("Error saving chat:", error);
        }
    };
       const stopStreaming = () => {
        if (eventSource) {
            eventSource.close();  // Close the EventSource connection
            setEventSource(null); // Reset the EventSource state
            console.log("Streaming stopped by the user.");
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.messages}>
                {messages.length > 0 ? (
                    messages.map((message, index) => (
                        <div key={index} className={styles.message}>
                            <strong>{message.from === 'user' ? 'You' : 'Bot'}:</strong>
                            <span>{message.text}</span>
                        </div>
                    ))
                ) : (
                    <div className={styles.startText}>
                        <h1>Ask a question!</h1>
                    </div>
                )}
            </div>
            <div className={styles.inputArea}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className={styles.input}
                    placeholder="Type a message..."
                    onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button onClick={sendMessage} className={styles.sendButton}>Send</button>
                <button onClick={stopStreaming} className={styles.stopButton}>Stop</button>

            </div>
        </div>
    );
}
