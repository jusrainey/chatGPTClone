'use client'
// use client
import { useState } from 'react';
import RootLayout from "@/app/layout";
import ChatHistory from '@/app/ChatHistory';
import CurrentChat from '@/app/CurrentChat';

export default function Home() {
  const [activeSession, setActiveSession] = useState(null);


  const handleSessionClick = (session) => {
    // If the session is new, create a session ID
    if (session.id === null) {
      const newSessionId = Date.now().toString(); // Simple ID generation for example purposes
      session.id = newSessionId;
      setActiveSession({ ...session });
      // In a real app, you'd make an API call to create a new session in the backend
    } else {
      setActiveSession(session);
    }
  };

  return (
    <RootLayout>
      <div style={{ display: 'flex', minHeight: '100vh' }}>
        <div style={{ width: '15%', backgroundColor: '#232222' }}>
          <ChatHistory setActiveSession={handleSessionClick} />
        </div>

        <div style={{ flexGrow: 1, backgroundColor: '#000000' }}>

          {activeSession && <CurrentChat activeSession={activeSession} setSessionId={setActiveSession} />}
        </div>
      </div>
    </RootLayout>
  );
}

