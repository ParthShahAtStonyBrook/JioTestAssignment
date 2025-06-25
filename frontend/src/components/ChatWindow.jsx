import { useState, useRef, useEffect } from 'react';
import {
  Box,
  VStack,
  Input,
  Button,
  Text,
  useToast,
  HStack,
  IconButton,
  Spinner,
  CloseButton,
  Heading,
  Select,
} from '@chakra-ui/react';
import { AttachmentIcon } from '@chakra-ui/icons';
import axios from 'axios';

const API_URL = 'http://localhost:5001';

const ChatWindow = ({ onClose }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [selectedItem, setSelectedItem] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const fileInputRef = useRef();
  const messagesEndRef = useRef();
  const toast = useToast();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    // Fetch orders when component mounts
    const fetchOrders = async () => {
      try {
        const response = await axios.get(`${API_URL}/orders`);
        setOrders(response.data);
      } catch (err) {
        console.error('Error fetching orders:', err);
        toast({
          title: 'Error',
          description: 'Failed to load orders. Please try again later.',
          status: 'error',
          duration: 5000,
        });
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();

    // Initialize chat with welcome message
    setMessages([
      {
        content: "👋 Welcome to Product Support! How can I help you today?",
        isUser: false,
        timestamp: new Date()
      },
      {
        content: "Type 'help' to see what I can do, or select an order to report an issue.",
        isUser: false,
        timestamp: new Date()
      }
    ]);
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const addMessage = (content, isUser = true) => {
    setMessages(prev => [...prev, { content, isUser, timestamp: new Date() }]);
  };

  const handleImageUpload = async (file) => {
    if (!file) {
      toast({
        title: 'Error',
        description: 'No image file selected.',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setIsAnalyzing(true);
    const formData = new FormData();
    formData.append('image', file);

    try {
      addMessage('🔄 Analyzing your image...', false);
      
      const response = await axios.post(`${API_URL}/analyze`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000,
      });

      if (response.data.error) {
        throw new Error(response.data.error);
      }

      const Analysis = response.data.analysis;
      const status = response.data.status;

      let responseMessage;
      if (status == 1) {
        responseMessage = [
          `🔍 Analysis Complete:`,
          `• Defect detected`,
          `• Analysis :` + Analysis,
        ].join('\n');
      } else {
        responseMessage = [
          `🔍 Analysis Complete:`,
          `• No defect detected`,
          `• Analysis :` + Analysis,
        ].join('\n');
      }

      addMessage(responseMessage, false);

    } catch (error) {
      console.error('Image analysis error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to analyze the image';
      addMessage(`❌ Error: ${errorMessage}`, false);
      toast({
        title: 'Analysis Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsAnalyzing(false);
      setSelectedImage(null);
    }
  };

  const handleOrderSelect = (event) => {
    const orderId = parseInt(event.target.value);
    const order = orders.find(o => o.id === orderId);
    setSelectedOrder(order);
    setSelectedItem(null);
    if (order) {
      addMessage(`Selected Order #${orderId}`, true);
      addMessage("Please select the item you'd like to report an issue with:", false);
    }
  };

  const handleItemSelect = (event) => {
    const itemId = parseInt(event.target.value);
    const item = selectedOrder.items.find(i => i.id === itemId);
    setSelectedItem(item);
    if (item) {
      addMessage(`Selected item: ${item.name}`, true);
      addMessage("Please upload a photo of the defective item.", false);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (!file.type.startsWith('image/')) {
        toast({
          title: 'Invalid File',
          description: 'Please select an image file.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      setSelectedImage(file);
      addMessage(`📎 Selected image: ${file.name}`);
      handleImageUpload(file);
    }
  };

  const handleTextCommand = async (text) => {
    try {
      const response = await axios.post(`${API_URL}/chat`, {
        message: text,
        order_id: selectedOrder?.id
      });

      const result = response.data;
      
      if (result.type === 'command') {
        // Handle special commands
        if (result.action === 'start_report') {
          // Reset selections to start fresh
          setSelectedOrder(null);
          setSelectedItem(null);
        }
      }
      
      addMessage(result.content, false);
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Failed to process your message';
      addMessage(`❌ Error: ${errorMessage}`, false);
      toast({
        title: 'Chat Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleSubmit = async () => {
    if (!inputMessage.trim() && !selectedImage) return;

    if (inputMessage.trim()) {
      addMessage(inputMessage);
      await handleTextCommand(inputMessage);
      setInputMessage('');
    }

    if (selectedImage) {
      await handleImageUpload(selectedImage);
    }
  };

  return (
    <Box
      bg="white"
      borderRadius="lg"
      shadow="lg"
      maxH="600px"
      w="100%"
      position="relative"
    >
      {/* Header */}
      <HStack
        p={4}
        borderBottomWidth={1}
        justify="space-between"
        bg="blue.500"
        color="white"
        borderTopRadius="lg"
      >
        <Heading size="sm">Product Support Chat</Heading>
        <CloseButton onClick={onClose} />
      </HStack>

      {/* Chat Messages */}
      <VStack
        spacing={4}
        p={4}
        overflowY="auto"
        maxH="400px"
        w="100%"
        css={{
          '&::-webkit-scrollbar': {
            width: '4px',
          },
          '&::-webkit-scrollbar-track': {
            width: '6px',
          },
          '&::-webkit-scrollbar-thumb': {
            background: 'gray.200',
            borderRadius: '24px',
          },
        }}
      >
        {messages.map((message, index) => (
          <Box
            key={index}
            bg={message.isUser ? 'blue.100' : 'gray.100'}
            p={3}
            borderRadius="lg"
            alignSelf={message.isUser ? 'flex-end' : 'flex-start'}
            maxW="80%"
          >
            <Text whiteSpace="pre-line">{message.content}</Text>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </VStack>

      {/* Input Section */}
      <Box p={4} borderTopWidth={1} w="100%" bg="gray.50">
        <VStack spacing={3}>
          <HStack w="100%">
            <Select 
              placeholder={loading ? "Loading orders..." : "Select Order"}
              value={selectedOrder?.id || ''} 
              onChange={handleOrderSelect}
              bg="white"
              isDisabled={loading}
            >
              {orders.map(order => (
                <option key={order.id} value={order.id}>
                  Order #{order.id} ({order.date})
                </option>
              ))}
            </Select>
            {selectedOrder && (
              <Select 
                placeholder="Select Item" 
                value={selectedItem?.id || ''} 
                onChange={handleItemSelect}
                bg="white"
              >
                {selectedOrder.items.map(item => (
                  <option key={item.id} value={item.id}>
                    {item.name} ($
                    {item.price !== undefined && item.price !== null ? item.price.toFixed(2) : 'N/A'})
                  </option>
                ))}
              </Select>
            )}
          </HStack>
          <HStack w="100%">
            <Input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              style={{ display: 'none' }}
              accept="image/*"
            />
            <IconButton
              icon={<AttachmentIcon />}
              onClick={() => fileInputRef.current.click()}
              aria-label="Upload image"
              isDisabled={isAnalyzing || !selectedItem}
            />
            <Input
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              onKeyPress={(e) => e.key === 'Enter' && !isAnalyzing && handleSubmit()}
              isDisabled={isAnalyzing}
              bg="white"
            />
            <Button 
              onClick={handleSubmit}
              colorScheme="blue"
              isDisabled={isAnalyzing || (!inputMessage.trim() && !selectedImage)}
              leftIcon={isAnalyzing ? <Spinner size="sm" /> : null}
            >
              {isAnalyzing ? 'Analyzing...' : 'Send'}
            </Button>
          </HStack>
        </VStack>
      </Box>
    </Box>
  );
};

export default ChatWindow; 