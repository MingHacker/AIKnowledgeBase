import React, { useState, useEffect, useRef } from 'react';
import { ChatSession, ChatMessage } from '../../types';
import apiService from '../../services/api';
import toast from 'react-hot-toast';
import {
  PaperAirplaneIcon,
  PlusIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  ClockIcon,
  UserCircleIcon,
  CpuChipIcon,
} from '@heroicons/react/24/outline';

interface ChatInterfaceProps {
  availableDocuments: string[];
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ availableDocuments }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadChatSessions();
  }, []);

  useEffect(() => {
    if (currentSession) {
      loadMessages(currentSession.id);
    }
  }, [currentSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadChatSessions = async () => {
    try {
      const data = await apiService.getChatSessions();
      setSessions(data);
      if (data.length > 0 && !currentSession) {
        setCurrentSession(data[0]);
      }
    } catch (error) {
      console.error('Failed to load chat sessions:', error);
      toast.error('Failed to load chat sessions');
    }
  };

  const loadMessages = async (sessionId: string) => {
    setMessagesLoading(true);
    try {
      const data = await apiService.getSessionMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast.error('Failed to load messages');
    } finally {
      setMessagesLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const session = await apiService.createChatSession();
      setSessions(prev => [session, ...prev]);
      setCurrentSession(session);
      setMessages([]);
    } catch (error) {
      console.error('Failed to create chat session:', error);
      toast.error('Failed to create new chat session');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSession || loading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    // Add user message immediately
    const newUserMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: currentSession.id,
      content: userMessage,
      message_type: 'user',
      source_chunks: [],
      created_at: new Date().toISOString(),
    };

    setMessages(prev => [...prev, newUserMessage]);

    try {
      const response = await apiService.askQuestion({
        question: userMessage,
        session_id: currentSession.id,
        document_filter: selectedDocuments,
        use_history: true,
      });

      // Remove temp message and add actual messages
      const aiMessage: ChatMessage = {
        id: response.message_id,
        session_id: currentSession.id,
        content: response.answer,
        message_type: 'assistant',
        source_chunks: response.sources.map(s => s.chunk_id),
        created_at: new Date().toISOString(),
      };

      setMessages(prev => [
        ...prev.filter(m => m.id !== newUserMessage.id),
        {
          ...newUserMessage,
          id: `user-${Date.now()}`, // We'll generate a user message ID
          source_chunks: [],
        },
        aiMessage,
      ]);

      // Update session with last message
      setSessions(prev =>
        prev.map(session =>
          session.id === currentSession.id
            ? { ...session, updated_at: new Date().toISOString() }
            : session
        )
      );
    } catch (error: any) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
      
      // Remove the temporary message on error
      setMessages(prev => prev.filter(m => m.id !== newUserMessage.id));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="h-full flex">
      {/* Sidebar */}
      <div className="w-64 bg-gray-50 border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <button
            onClick={createNewSession}
            className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Recent Chats</h3>
          <div className="space-y-2">
            {sessions.map((session) => (
              <button
                key={session.id}
                onClick={() => setCurrentSession(session)}
                className={`w-full text-left p-3 rounded-lg transition-colors ${
                  currentSession?.id === session.id
                    ? 'bg-primary-50 border border-primary-200'
                    : 'hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center">
                  <ChatBubbleLeftRightIcon className="h-4 w-4 text-gray-400 mr-2" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {session.title || 'New Chat'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatDate(session.updated_at)}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Document Filter */}
        <div className="p-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Filter by Documents</h4>
          <div className="max-h-32 overflow-y-auto space-y-1">
            {availableDocuments.map((docId) => (
              <label key={docId} className="flex items-center">
                <input
                  type="checkbox"
                  checked={selectedDocuments.includes(docId)}
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedDocuments(prev => [...prev, docId]);
                    } else {
                      setSelectedDocuments(prev => prev.filter(id => id !== docId));
                    }
                  }}
                  className="h-3 w-3 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-xs text-gray-600 truncate">
                  Document {docId.slice(0, 8)}...
                </span>
              </label>
            ))}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* Chat Header */}
            <div className="px-6 py-4 border-b border-gray-200 bg-white">
              <div className="flex items-center">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-gray-400 mr-3" />
                <div>
                  <h1 className="text-lg font-medium text-gray-900">
                    {currentSession.title || 'New Chat'}
                  </h1>
                  <p className="text-sm text-gray-500">
                    {selectedDocuments.length > 0
                      ? `Searching in ${selectedDocuments.length} document(s)`
                      : 'Searching in all documents'
                    }
                  </p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messagesLoading ? (
                <div className="flex items-center justify-center py-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  <span className="ml-2 text-gray-600">Loading messages...</span>
                </div>
              ) : messages.length === 0 ? (
                <div className="text-center py-8">
                  <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No messages yet</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Start a conversation by asking a question about your documents.
                  </p>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${
                      message.message_type === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    <div
                      className={`max-w-3xl flex ${
                        message.message_type === 'user' ? 'flex-row-reverse' : 'flex-row'
                      }`}
                    >
                      <div
                        className={`flex-shrink-0 ${
                          message.message_type === 'user' ? 'ml-3' : 'mr-3'
                        }`}
                      >
                        {message.message_type === 'user' ? (
                          <UserCircleIcon className="h-8 w-8 text-primary-600" />
                        ) : (
                          <CpuChipIcon className="h-8 w-8 text-gray-600" />
                        )}
                      </div>
                      <div
                        className={`px-4 py-2 rounded-lg ${
                          message.message_type === 'user'
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <div className="whitespace-pre-wrap">{message.content}</div>
                        <div
                          className={`text-xs mt-1 flex items-center ${
                            message.message_type === 'user'
                              ? 'text-primary-100'
                              : 'text-gray-500'
                          }`}
                        >
                          <ClockIcon className="h-3 w-3 mr-1" />
                          {formatTime(message.created_at)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="max-w-3xl flex">
                    <div className="mr-3">
                      <CpuChipIcon className="h-8 w-8 text-gray-600" />
                    </div>
                    <div className="px-4 py-2 rounded-lg bg-gray-100">
                      <div className="flex items-center space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="px-6 py-4 border-t border-gray-200 bg-white">
              <div className="flex items-end space-x-3">
                <div className="flex-1">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask a question about your documents..."
                    rows={1}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm resize-none"
                    style={{ minHeight: '40px', maxHeight: '120px' }}
                  />
                </div>
                <button
                  onClick={sendMessage}
                  disabled={!inputMessage.trim() || loading}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <PaperAirplaneIcon className="h-4 w-4" />
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center">
            <div className="text-center">
              <ChatBubbleLeftRightIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No chat selected</h3>
              <p className="mt-1 text-sm text-gray-500">
                Create a new chat to start asking questions about your documents.
              </p>
              <button
                onClick={createNewSession}
                className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <PlusIcon className="h-4 w-4 mr-2" />
                Start New Chat
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;