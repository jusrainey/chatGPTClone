import { useState, useEffect } from 'react';
import styles from './CurrentChat.module.css';

export default function ChatHistory({ setActiveSession, activeSessionId }) {
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchSessions();
        handleNewSession();// Function to fetch existing sessions
    }, []);

    useEffect(() => {
    const intervalId = setInterval(() => {
        fetchSessions()
    }, 10000); // Update every 10 seconds

    return () => clearInterval(intervalId);
}, []);

    const fetchSessions = async () => {
        const response = await fetch('http://127.0.0.1:5000/get_sessions');
        const data = await response.json();
        setSessions(data.sessions);
    };

    const handleNewSession = async () => {
        setLoading(true);
        const response = await fetch('http://127.0.0.1:5000/new_session_id');
        const data = await response.json();
        const newSessionId = data.next_session_id;
        setActiveSession({ id: newSessionId, name: `Session ${newSessionId}` });
        setLoading(false);

    };

    const deleteSession = async (sessionId) => {
    setLoading(true);
    console.log('Deleting Session:',sessionId)
    try {
        // Correct the URL format
        await fetch(`http://127.0.0.1:5000/delete_session?session_id=${sessionId}`, { method: 'DELETE' });
        handleNewSession();  // Refresh the list or create a new session
    } catch (error) {
        console.error('Error deleting session:', error);
    }
    setLoading(false);
};


    return (
        <div className='chatHistory'>
            <button onClick={handleNewSession} disabled={loading} className={styles.newSessionButton}>
                {loading ? 'Loading...' : 'New Session'}
            </button>
            {sessions.map(session => (
                <div key={session.id} onClick={() => setActiveSession(session)} className='sessionItem'>
                    {session.name}
                       <button
                        className="deleteButton"
                        onClick={(e) => {
                            e.stopPropagation();  // Prevent activating the session
                            deleteSession(session.id);
                        }}
                    >
                        Delete
                    </button>
                </div>
            ))}
        </div>
    );
}
