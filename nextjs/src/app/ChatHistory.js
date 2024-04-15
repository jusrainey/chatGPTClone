// This seems fine as is. Clicking on a session sets the active session.
export default function ChatHistory({ sessions, setActiveSession }) {
  return (
    <div className='chatHistory'>
      {sessions.map((session) => (
        <div key={session.id} onClick={() => setActiveSession(session)} className='sessionItem'>
          {session.name}
        </div>
      ))}
    </div>
  );
}
