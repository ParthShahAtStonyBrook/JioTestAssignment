import { Box, VStack, Heading, Text, Badge, SimpleGrid, HStack, Icon } from '@chakra-ui/react';
import { FaBox, FaCalendarAlt, FaDollarSign } from 'react-icons/fa';

export const dummyOrders = [
  {
    id: 1,
    date: '2025-06-01',
    items: [
      { id: 101, name: 'Wireless Headphones', price: 99.99 },
      { id: 102, name: 'Smart Watch', price: 199.99 }
    ],
    status: 'Delivered'
  },
  {
    id: 2,
    date: '2025-05-28',
    items: [
      { id: 201, name: 'Laptop Stand', price: 49.99 },
      { id: 202, name: 'Keyboard', price: 79.99 }
    ],
    status: 'Delivered'
  },
  {
    id: 3,
    date: '2025-05-25',
    items: [
      { id: 301, name: 'Monitor', price: 299.99 }
    ],
    status: 'Delivered'
  }
];

const OrderList = () => {
  return (
    <Box p={{ base: 4, md: 6, lg: 8 }}>
      <Heading 
        size="lg" 
        mb={6} 
        color="blue.700"
        textAlign="center"
      >
        Your Orders
      </Heading>
      <VStack spacing={6} align="stretch" maxW="800px" mx="auto">
        {dummyOrders.map((order) => (
          <Box 
            key={order.id}
            p={{ base: 4, md: 6 }}
            borderWidth={1}
            borderRadius="xl"
            shadow="md"
            bg="white"
            _hover={{ shadow: 'lg' }}
            transition="all 0.2s"
          >
            <HStack 
              justify="space-between" 
              mb={4}
              flexWrap={{ base: "wrap", md: "nowrap" }}
              spacing={4}
            >
              <HStack spacing={4}>
                <Icon as={FaBox} color="blue.500" boxSize={5} />
                <Text fontWeight="bold" fontSize={{ base: "md", md: "lg" }}>
                  Order #{order.id}
                </Text>
              </HStack>
              <Badge 
                colorScheme="green" 
                p={2} 
                borderRadius="md"
                fontSize={{ base: "xs", md: "sm" }}
              >
                {order.status}
              </Badge>
            </HStack>
            
            <HStack 
              spacing={{ base: 4, md: 6 }} 
              mb={4} 
              color="gray.600"
              flexWrap={{ base: "wrap", md: "nowrap" }}
            >
              <HStack>
                <Icon as={FaCalendarAlt} />
                <Text fontSize={{ base: "sm", md: "md" }}>{order.date}</Text>
              </HStack>
              <HStack>
                <Icon as={FaDollarSign} />
                <Text fontSize={{ base: "sm", md: "md" }}>
                  Total: ${order.items.reduce((sum, item) => sum + item.price, 0).toFixed(2)}
                </Text>
              </HStack>
            </HStack>
            
            <SimpleGrid 
              columns={{ base: 1, md: 2 }} 
              spacing={4} 
              mt={4}
            >
              {order.items.map((item) => (
                <Box 
                  key={item.id}
                  p={4}
                  borderWidth={1}
                  borderRadius="lg"
                  bg="gray.50"
                >
                  <VStack align="start" spacing={1}>
                    <Text fontWeight="medium">{item.name}</Text>
                    <Text fontSize="sm" color="gray.600">${item.price}</Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </Box>
        ))}
      </VStack>
    </Box>
  );
};

export default OrderList; 