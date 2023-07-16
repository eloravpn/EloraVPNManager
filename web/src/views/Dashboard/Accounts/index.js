import React, { useEffect, useState } from "react";
import {
  Form,
  Link,
  json,
  useActionData,
  useFetcher,
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
  FormControl,
  FormLabel,
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
  Switch,
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
import UserModal from "../Users/components/UserModal";
import AccountModal from "../Users/components/AccountModal";
import { AccountAPI } from "../../../api/AccountAPI";
import User from "./components/User";

const Accounts = ({ data }) => {
  const navigate = useNavigate();




  const fetcher = useFetcher();

  const [accounts, setAccounts] = useState();

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

  const [q, setQ] = useState();

  const handleQChange = (event) => setQ(event.target.value);

  const [enable, setEnable] = useState(true);
  const handleEnableChange = (event) => {
    console.log(event);
    setEnable(event.target.checked);
  };

  const search = (items) => {
    return items.filter((item) => {
      let searchQuery = q || "";
      let enableFilter = item.enable == enable;
      return (
        enableFilter &
        (JSON.stringify(item).toLowerCase().indexOf(searchQuery.toLowerCase()) >
          -1)
      );
    });
  };

  const units = [
    "bytes",
    "KiB",
    "MiB",
    "GiB",
    "TiB",
    "PiB",
    "EiB",
    "ZiB",
    "YiB",
  ];

  function niceBytes(x) {
    let l = 0,
      n = parseInt(x, 10) || 0;

    while (n >= 1024 && ++l) {
      n = n / 1024;
    }

    return n.toFixed(n < 10 && l > 0 ? 1 : 0) + " " + units[l];
  }

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

  const fetchAccounts = () => {
    AccountAPI.getAll().then((res) => {
      setAccounts(res);
    });
  };

  useEffect(() => {
    fetchAccounts();
    const interval = setInterval(fetchAccounts, 5000);

    return () => clearInterval(interval);
  }, [enable]);

  useEffect(() => {
    const interval = setInterval(() => {
      // navigate();
    }, 5000);

    return () => clearInterval(interval);
  }, [fetcher]);

  return (
    <VStack spacing={4} p={5} align="stretch">
      {/* <UserModal
        isOpen={isEditOpen}
        onClose={onEditClose}
        btnRef={btnRef}
        user={user}
      /> */}
      <AccountModal
        isOpen={isEditAccountOpen}
        onClose={onEditAccountClose}
        btnRef={btnRef}
        user={user}
        account={account}
        redirect={"/admin/accounts"}
      />
      >
      <Box>
        <Heading as="h3" size="lg">
          Accounts
        </Heading>
      </Box>
      <Box>
        <Button
          leftIcon={<AddIcon />}
          ref={btnRef}
          colorScheme="teal"
          onClick={() => {
            setAccount();
            onEditAccountOpen();
          }}
        >
          Create User
        </Button>
      </Box>
      <Stack spacing={5} direction="row">
        <Input
          onChange={handleQChange}
          value={q}
          type="text"
          placeholder="Search"
        />

        <FormLabel htmlFor="enable" mb="0">
          Enable?
        </FormLabel>
        <Switch
          isChecked={enable}
          onChange={handleEnableChange}
        // onBlur={formik.handleBlur}
        />
      </Stack>
      <Box>
        <FormControl></FormControl>
      </Box>
      <Box>
        {accounts && accounts.length ? (
          <TableContainer>
            <Table variant="striped" colorScheme="teal">
              <Thead>
                <Tr>
                  <Th>UUID</Th>
                  <Th>Email</Th>
                  <Th>User</Th>
                  <Th>Usage</Th>
                  <Th>Enable</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {search(accounts).map((account) => (
                  <Tr key={account.id}>
                    <Td>{account.uuid} </Td>
                    <Td>{account.email}</Td>
                    <Td>
                      <User userId={account.user_id} />
                    </Td>
                    <Td>
                      {niceBytes(account.used_traffic)} /{" "}
                      {niceBytes(account.data_limit)}
                    </Td>
                    <Td>
                      {account.enable ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>

                    {/* <Td></Td> */}

                    <Td>
                      <Menu>
                        <MenuButton as={Button} rightIcon={<ChevronDownIcon />}>
                          <SettingsIcon />
                        </MenuButton>

                        <MenuList>
                          <MenuItem
                            icon={<DeleteIcon />}
                            onClick={() => {
                              delteAccount(account.id);
                            }}
                          >
                            Delete
                          </MenuItem>
                          <MenuItem
                            icon={<EditIcon />}
                            onClick={() => {
                              setAccount(account);
                              onEditAccountOpen();
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

export default Accounts;
