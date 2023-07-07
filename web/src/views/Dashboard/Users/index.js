import React, { useState } from "react";
import {
  Form,
  Link,
  useActionData,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Box,
  Button,
  Drawer,
  DrawerBody,
  DrawerCloseButton,
  DrawerContent,
  DrawerFooter,
  DrawerHeader,
  DrawerOverlay,
  Heading,
  Input,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Modal,
  ModalBody,
  ModalCloseButton,
  ModalFooter,
  ModalHeader,
  ModalOverlay,
  Stack,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import {
  AddIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  DeleteIcon,
  EditIcon,
  EmailIcon,
  NotAllowedIcon,
  SettingsIcon,
} from "@chakra-ui/icons";
import UserModal from "./components/UserModal";

const Users = ({ data }) => {
  const navigate = useNavigate();

  let location = useLocation();
  let actionData = useActionData();
  const [hostId, setHostId] = useState();

  const [user, setUser] = useState();

  const { isOpen, onOpen, onClose, getButtonProps } = useDisclosure();

  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure();

  const buttonProps = getButtonProps();

  const cancelRef = React.useRef();

  const btnRef = React.useRef();

  return (
    <VStack spacing={4} p={5} align="stretch">
      <UserModal
        isOpen={isEditOpen}
        onClose={onEditClose}
        btnRef={btnRef}
        user={user}
      />

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete {user ? user.first_name + " " + user.last_name : ""}
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure? You can't undo this action afterwards.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onClose}>
                Cancel
              </Button>

              <Form
                method="post"
                action={`user/${user ? user.id : 0}/destroy`}
                onSubmit={onClose}
              >
                <Button colorScheme="red" type={"submit"} ml={3}>
                  Delete
                </Button>
              </Form>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>

      <Box>
        <Heading as="h3" size="lg">
          Users
        </Heading>
      </Box>

      <Box>
        <Button
          leftIcon={<AddIcon />}
          ref={btnRef}
          colorScheme="teal"
          onClick={() => {
            setUser(null);
            onEditOpen();
          }}
        >
          Create User
        </Button>
      </Box>

      <Box>
        {data.length ? (
          <TableContainer>
            <Table variant="striped" colorScheme="teal">
              <Thead>
                <Tr>
                  <Th>Name</Th>
                  <Th>Username</Th>
                  <Th>TG Username</Th>
                  <Th>TG Chat Id</Th>
                  <Th>Enable</Th>
                  <Th>Banned</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data.map((user) => (
                  <Tr key={user.id}>
                    <Td>{user.first_name + " " + user.last_name}</Td>
                    <Td>{user.username}</Td>
                    <Td>{user.telegram_chat_id}</Td>
                    <Td>{user.telegram_username}</Td>
                    <Td>
                      {user.enable ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>
                    <Td>
                      {user.banned ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>

                    <Td>
                      <Menu>
                        <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
                          <SettingsIcon />
                        </MenuButton>

                        <MenuList>
                          <MenuItem
                            icon={<DeleteIcon />}
                            onClick={() => {
                              setUser(user);
                              onOpen();
                            }}
                          >
                            Delete
                          </MenuItem>
                          <MenuItem
                            icon={<EditIcon />}
                            onClick={() => {
                              setUser(user);
                              onEditOpen();
                            }}
                          >
                            Edit
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </TableContainer>
        ) : (
          <div>No Users</div>
        )}
      </Box>
    </VStack>
  );
};

export default Users;
