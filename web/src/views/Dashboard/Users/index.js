import React, { useState } from "react";
import {
  Form,
  Link,
  useActionData,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Accordion,
  AccordionButton,
  AccordionIcon,
  AccordionItem,
  AccordionPanel,
  AlertDialog,
  AlertDialogBody,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogOverlay,
  Badge,
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
  IconButton,
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
import AccountModal from "./components/AccountModal";
import { AccountAPI } from "../../../api/AccountAPI";

const Users = ({ data }) => {
  const navigate = useNavigate();

  let location = useLocation();
  let actionData = useActionData();
  const [hostId, setHostId] = useState();
  const [account, setAccount] = useState();

  const delteAccount = (id) => {
    if (window.confirm("Are you sure to delete this account?")) {
      AccountAPI.delete(id).then(() => {
        navigate();
      });
    }
  };

  const [user, setUser] = useState();

  const { isOpen, onOpen, onClose, getButtonProps } = useDisclosure();

  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure();

  const {
    isOpen: isEditAccountOpen,
    onOpen: onEditAccountOpen,
    onClose: onEditAccountClose,
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

      <AccountModal
        isOpen={isEditAccountOpen}
        onClose={onEditAccountClose}
        btnRef={btnRef}
        user={user}
        account={account}
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
                    <Td>
                      <Accordion allowToggle>
                        <AccordionItem>
                          <h2>
                            <AccordionButton>
                              <Box as="span" flex="1" textAlign="left">
                                {user.first_name + " " + user.last_name}
                                {user.accounts.length ? (
                                  <Badge m={2} colorScheme="purple">
                                    {user.accounts.length} Accounts
                                  </Badge>
                                ) : (
                                  ""
                                )}
                              </Box>
                              <AccordionIcon />
                            </AccordionButton>
                          </h2>
                          <AccordionPanel pb={4}>
                            {user.accounts.length ? (
                              <TableContainer>
                                <Table variant="striped" colorScheme="teal">
                                  <Thead>
                                    <Tr>
                                      <Th>Email</Th>
                                      <Th>Data</Th>
                                      <Th>Expire</Th>

                                      <Th>Action</Th>
                                    </Tr>
                                  </Thead>
                                  <Tbody>
                                    {user.accounts.map((account) => (
                                      <Tr
                                        key={account.id}
                                        color={account.enable ? "" : "red.500"}
                                      >
                                        <Td>
                                          {account.email}
                                          {account.enable ? (
                                            ""
                                          ) : (
                                            <Badge color={"red.400"}>
                                              Disabled
                                            </Badge>
                                          )}
                                        </Td>

                                        <Td>{account.data_limit} </Td>
                                        <Td>
                                          {new Date(
                                            account.expired_at
                                          ).toLocaleDateString(
                                            "fa-IR-u-nu-latn"
                                          )}{" "}
                                        </Td>

                                        <Td>
                                          <IconButton
                                            mr={2}
                                            onClick={() => {
                                              setAccount(account);
                                              onEditAccountOpen();
                                            }}
                                            size="sm"
                                            icon={<EditIcon />}
                                          />
                                          <IconButton
                                            mr={2}
                                            onClick={() => {
                                              // setAccount(account);

                                              delteAccount(account.id);

                                              // onEditAccountOpen();
                                            }}
                                            size="sm"
                                            icon={<DeleteIcon />}
                                          />
                                        </Td>
                                      </Tr>
                                    ))}
                                  </Tbody>
                                </Table>
                              </TableContainer>
                            ) : (
                              "No accounts"
                            )}
                          </AccordionPanel>
                        </AccordionItem>
                      </Accordion>
                    </Td>
                    <Td>{user.username} </Td>
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
                            icon={<AddIcon />}
                            onClick={() => {
                              setAccount();
                              setUser(user);
                              onEditAccountOpen();
                            }}
                          >
                            Add Acccount
                          </MenuItem>
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
