import { IconButton, Box, useDisclosure } from '@chakra-ui/react';
import { ChatIcon } from '@chakra-ui/icons';
import ChatWindow from './ChatWindow';

const FloatingChatButton = () => {
  const { isOpen, onToggle } = useDisclosure();

  return (
    <Box position="fixed" bottom="4" right="4" zIndex="999">
      {isOpen && (
        <Box position="absolute" bottom="16" right="0" width="400px">
          <ChatWindow onClose={onToggle} />
        </Box>
      )}
      <IconButton
        icon={<ChatIcon />}
        colorScheme="blue"
        size="lg"
        rounded="full"
        shadow="lg"
        onClick={onToggle}
        aria-label="Open chat"
      />
    </Box>
  );
};

export default FloatingChatButton; 