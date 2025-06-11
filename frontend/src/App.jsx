import { useState, useEffect } from 'react';
import { ChakraProvider, Container, Heading, Box, useToast, Grid, GridItem } from '@chakra-ui/react'
import FloatingChatButton from './components/FloatingChatButton'
import OrderList from './components/OrderList'
import LoginPage from './components/LoginPage'
import axios from 'axios'

function App() {
  const toast = useToast();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for existing token
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token validity
      checkAuth();
    } else {
      setIsLoading(false);
    }
  }, []);

  const checkAuth = async () => {
    try {
      const response = await axios.get('http://localhost:5001/api/auth/user');
      if (response.data) {
        setIsAuthenticated(true);
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      toast({
        title: 'Authentication Error',
        description: 'Your session has expired. Please log in again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setIsAuthenticated(false);
  };

  if (isLoading) {
    return (
      <ChakraProvider>
        <Box minH="100vh" bg="gray.100" display="flex" alignItems="center" justifyContent="center">
          <Heading size="lg" color="gray.500">Loading...</Heading>
        </Box>
      </ChakraProvider>
    );
  }

  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.100">
        {!isAuthenticated ? (
          <LoginPage onLoginSuccess={handleLoginSuccess} />
        ) : (
          <>
            <Box p={4}>
              <OrderList onLogout={handleLogout} />
            </Box>
            <FloatingChatButton />
          </>
        )}
      </Box>
    </ChakraProvider>
  )
}

export default App
