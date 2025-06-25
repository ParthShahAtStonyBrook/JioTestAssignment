import { Box, VStack, Heading, Text, Badge, SimpleGrid, HStack, Icon, Spinner, Button, Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react';
import { FaBox, FaCalendarAlt, FaDollarSign } from 'react-icons/fa';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { useToast } from '@chakra-ui/react';

const API_URL = 'http://localhost:5001';

// Keep the dummy data for reference but don't use it

const OrderList = ({ onLogout }) => {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const toast = useToast();

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API_URL}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Error fetching orders:', error);
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

  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
      </Box>
    );
  }

  return (
    <Box bg="white" borderRadius="lg" shadow="md" overflow="hidden">
      <Box p={4} borderBottomWidth={1}>
        <HStack justify="space-between">
          <Heading size="md">Your Orders</Heading>
          <Button
            colorScheme="red"
            variant="outline"
            size="sm"
            onClick={onLogout}
          >
            Logout
          </Button>
        </HStack>
      </Box>

      {orders.length === 0 ? (
        <Box p={4} textAlign="center">
          <Text color="gray.500">No orders found</Text>
        </Box>
      ) : (
        <Table variant="simple">
          <Thead>
            <Tr>
              <Th>Order ID</Th>
              <Th>Date</Th>
              <Th>Status</Th>
              <Th>Items</Th>
            </Tr>
          </Thead>
          <Tbody>
            {orders.map((order) => (
              <Tr key={order.id}>
                <Td>#{order.id}</Td>
                <Td>{new Date(order.date).toLocaleDateString()}</Td>
                <Td>
                  <Badge
                    colorScheme={
                      order.status === 'Delivered'
                        ? 'green'
                        : order.status === 'Pending'
                        ? 'yellow'
                        : 'blue'
                    }
                  >
                    {order.status}
                  </Badge>
                </Td>
                <Td>
                  <Text noOfLines={2}>
                    {order.items.map((item) => `${item.name} ($${item.price?.toFixed(2) ?? 'N/A'})`).join(', ')}
                  </Text>
                </Td>
              </Tr>
            ))}
          </Tbody>
        </Table>
      )}
    </Box>
  );
};

export default OrderList; 