import { ChakraProvider, Container, Heading, Box, useToast, Grid, GridItem } from '@chakra-ui/react'
import FloatingChatButton from './components/FloatingChatButton'
import OrderList from './components/OrderList'

function App() {
  const toast = useToast();

  const handleSelectItem = (orderId, item) => {
    toast({
      title: 'Item Selected',
      description: `Selected ${item.name} from Order #${orderId}`,
      status: 'info',
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50" py={8}>
        <Container maxW="container.xl">
          <Grid templateColumns="repeat(12, 1fr)" gap={6}>
            <GridItem colSpan={12}>
              <Heading 
                textAlign="center" 
                mb={8} 
                color="blue.600"
                fontSize={{ base: "2xl", md: "3xl", lg: "4xl" }}
                fontWeight="bold"
              >
                Product Defect Detection System
              </Heading>
            </GridItem>
            
            <GridItem 
              colSpan={{ base: 12, md: 10, lg: 8 }} 
              colStart={{ base: 1, md: 2, lg: 3 }}
            >
              <Box 
                bg="white" 
                borderRadius="xl" 
                shadow="lg"
                overflow="hidden"
                mx="auto"
              >
                <OrderList onSelectItem={handleSelectItem} />
              </Box>
            </GridItem>
          </Grid>
        </Container>
        <FloatingChatButton />
      </Box>
    </ChakraProvider>
  )
}

export default App
