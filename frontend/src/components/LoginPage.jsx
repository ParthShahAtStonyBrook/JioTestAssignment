import { useState } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Heading,
  Text,
  useToast,
  Container,
  Tab,
  TabList,
  TabPanel,
  TabPanels,
  Tabs,
} from '@chakra-ui/react';
import axios from 'axios';

const API_URL = 'http://localhost:5001';

const LoginPage = ({ onLoginSuccess }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const toast = useToast();

  // Login form state
  const [loginForm, setLoginForm] = useState({
    username: '',
    password: '',
  });

  // Register form state
  const [registerForm, setRegisterForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/api/auth/login`, loginForm);
      const { access_token } = response.data;
      
      // Store the token
      localStorage.setItem('token', access_token);
      
      // Set the default Authorization header for all future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Notify success
      toast({
        title: 'Login Successful',
        status: 'success',
        duration: 3000,
      });

      // Call the success callback
      onLoginSuccess();

    } catch (error) {
      toast({
        title: 'Login Failed',
        description: error.response?.data?.error || 'An error occurred',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    // Validate passwords match
    if (registerForm.password !== registerForm.confirmPassword) {
      toast({
        title: 'Registration Failed',
        description: 'Passwords do not match',
        status: 'error',
        duration: 5000,
      });
      setIsLoading(false);
      return;
    }

    try {
      const { confirmPassword, ...registrationData } = registerForm;
      const response = await axios.post(`${API_URL}/api/auth/register`, registrationData);
      const { access_token } = response.data;
      
      // Store the token
      localStorage.setItem('token', access_token);
      
      // Set the default Authorization header for all future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Notify success
      toast({
        title: 'Registration Successful',
        status: 'success',
        duration: 3000,
      });

      // Call the success callback
      onLoginSuccess();

    } catch (error) {
      toast({
        title: 'Registration Failed',
        description: error.response?.data?.error || 'An error occurred',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxW="md" py={12}>
      <Box bg="white" p={8} borderRadius="lg" boxShadow="xl">
        <Tabs isFitted index={activeTab} onChange={setActiveTab}>
          <TabList mb={4}>
            <Tab>Login</Tab>
            <Tab>Register</Tab>
          </TabList>

          <TabPanels>
            {/* Login Panel */}
            <TabPanel>
              <VStack as="form" spacing={4} onSubmit={handleLogin}>
                <Heading size="lg">Welcome Back</Heading>
                <Text color="gray.600">Please sign in to continue</Text>

                <FormControl isRequired>
                  <FormLabel>Username</FormLabel>
                  <Input
                    type="text"
                    value={loginForm.username}
                    onChange={(e) => setLoginForm({ ...loginForm, username: e.target.value })}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <Input
                    type="password"
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                  />
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  width="full"
                  mt={4}
                  isLoading={isLoading}
                >
                  Sign In
                </Button>
              </VStack>
            </TabPanel>

            {/* Register Panel */}
            <TabPanel>
              <VStack as="form" spacing={4} onSubmit={handleRegister}>
                <Heading size="lg">Create Account</Heading>
                <Text color="gray.600">Please fill in your details</Text>

                <FormControl isRequired>
                  <FormLabel>Username</FormLabel>
                  <Input
                    type="text"
                    value={registerForm.username}
                    onChange={(e) => setRegisterForm({ ...registerForm, username: e.target.value })}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Email</FormLabel>
                  <Input
                    type="email"
                    value={registerForm.email}
                    onChange={(e) => setRegisterForm({ ...registerForm, email: e.target.value })}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Password</FormLabel>
                  <Input
                    type="password"
                    value={registerForm.password}
                    onChange={(e) => setRegisterForm({ ...registerForm, password: e.target.value })}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Confirm Password</FormLabel>
                  <Input
                    type="password"
                    value={registerForm.confirmPassword}
                    onChange={(e) => setRegisterForm({ ...registerForm, confirmPassword: e.target.value })}
                  />
                </FormControl>

                <Button
                  type="submit"
                  colorScheme="blue"
                  width="full"
                  mt={4}
                  isLoading={isLoading}
                >
                  Create Account
                </Button>
              </VStack>
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Container>
  );
};

export default LoginPage; 