import React, { useContext } from 'react';
import { useParams } from 'react-router-dom';
import ChatInterface from '../components/ChatInterface';

const CustomerChat = () => {
  const { serviceId } = useParams(); // Get service ID from URL
  
  return (
    <div className="h-screen">
      <ChatInterface 
        serviceId={serviceId} 
        embedMode={false}
      />
    </div>
  );
};

export default CustomerChat;