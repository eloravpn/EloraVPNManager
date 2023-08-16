/* eslint-disable no-unused-vars */
import React, { useEffect, useState } from "react";
import {
  useActionData,
  useFetcher,
  useLocation,
  useNavigate,
} from "react-router-dom";
import {
  Badge,
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
  HStack,
  Input,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Select,
  Stack,
  Switch,
  Table,
  TableContainer,
  Tag,
  TagLabel,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  useDisclosure,
  VStack,
} from "@chakra-ui/react";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ChevronDownIcon,
  DeleteIcon,
  EditIcon,
  NotAllowedIcon,
  RepeatIcon,
  SettingsIcon,
} from "@chakra-ui/icons";
import AccountModal from "../Users/components/AccountModal";
import { AccountAPI } from "../../../api/AccountAPI";
import User from "./components/User";
import ReactPaginate from "react-paginate";
import "../../../assets/styles/pagination.css";

const Accounts = () => {
  const navigate = useNavigate();

  const [accounts, setAccounts] = useState();
  const [total, setTotal] = useState();
  const [accountsReport, setaccountsReport] = useState();

  const [hostId, setHostId] = useState();
  const [account, setAccount] = useState();

  const delteAccount = (id) => {
    if (window.confirm("Are you sure to delete this account?")) {
      AccountAPI.delete(id).then(() => {
        navigate();
      });
    }
  };

  const resetTraffic = (id) => {
    if (window.confirm("Are you sure to rested traffic this account?")) {
      AccountAPI.reseteTraffic(id).then(() => {
        navigate();
      });
    }
  };

  const [q, setQ] = useState();
  const [rows, setRows] = useState(20);
  const [sort, setSort] = useState("expire");

  const handleQChange = (event) => {
    setQ(event.target.value);
    setOffset(0);
    setCurPage(1);
  };

  const [enable, setEnable] = useState(true);
  const handleEnableChange = (event) => {
    setEnable(event.target.checked);
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
  const [offset, setOffset] = useState();
  const [curPage, setCurPage] = useState(0);

  const { getButtonProps } = useDisclosure();

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

  const btnRef = React.useRef();

  const fetchAccounts = () => {
    AccountAPI.getAll(rows, sort, enable, offset, q).then((res) => {
      setTotal(res.total);
      setAccounts(res.accounts);
    });
  };

  const fetchAccountsReport = () => {
    AccountAPI.getAccountsReport().then((res) => {
      setaccountsReport(res);
    });
  };

  const handlePageClick = (data) => {
    let selected = data.selected;
    let offset = Math.ceil(selected * rows);
    setOffset(offset);
    setCurPage(selected);
  };

  useEffect(() => {
    fetchAccounts();
    const interval = setInterval(fetchAccounts, 5000);

    return () => clearInterval(interval);
  }, [enable, rows, sort, offset, q]);

  useEffect(() => {
    fetchAccountsReport();
    const interval = setInterval(fetchAccountsReport, 5000);

    return () => clearInterval(interval);
  }, []);

  // useEffect(() => {
  //   const interval = setInterval(() => {
  //     // navigate();
  //   }, 5000);

  //   return () => clearInterval(interval);
  // }, [fetcher]);

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

      <Box>
        <Heading as="h3" size="lg">
          Accounts
        </Heading>

        {!accountsReport ? (
          ""
        ) : (
          <HStack>
            <Tag colorScheme="green">Active: {accountsReport.active}</Tag>
            <Tag colorScheme="red">
              Disabled: {accountsReport.total - accountsReport.active}
            </Tag>
            <Tag colorScheme="blue">Total: {accountsReport.total}</Tag>
          </HStack>
        )}
      </Box>
      {/* <Box>
        <Button
          leftIcon={<AddIcon />}
          ref={btnRef}
          // colorScheme="teal"
          onClick={() => {
            setAccount();
            onEditAccountOpen();
          }}
        >
          Create User
        </Button>
      </Box> */}
      <Stack spacing={5} direction={{ sm: "column", md: "row" }}>
        <Box w={{ base: "50%", sm: "100%" }}>
          <Input
            onChange={handleQChange}
            value={q}
            type="text"
            placeholder="Search"
          />
        </Box>

        <Stack
          w={{ base: "50%", sm: "100%" }}
          direction={{ base: "row", md: "row", sm: "column" }}
        >
          <FormLabel htmlFor="enable" mb="0">
            Enable?
          </FormLabel>
          <Switch isChecked={enable} onChange={handleEnableChange} />
          <Select
            placeholder="Rows"
            onChange={(event) => {
              setRows(event.target.value);
            }}
            defaultValue={rows}
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
          </Select>
          <Select
            placeholder="Sort by"
            onChange={(event) => {
              setSort(event.target.value);
            }}
            defaultValue={sort}
          >
            <option value="expire">Expire ASC</option>
            <option value="-expire">Expire DESC</option>
            <option value="used-traffic-percent">Used traffic% ASC</option>
            <option value="-used-traffic-percent">Used traffic% DESC</option>
            <option value="created">Created ASC</option>
            <option value="-created">Created DESC</option>
            <option value="modified">Modified ASC</option>
            <option value="-modified">Modified DESC</option>
            <option value="used-traffic">Used traffic ASC</option>
            <option value="-used-traffic">Used traffic DESC</option>
            <option value="data-limit">Data limit ASC</option>
            <option value="-data-limit">Data limit DESC</option>
          </Select>
        </Stack>
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
                  <Th display={{ sm: "None" }}>UUID</Th>
                  {/* <Th>Email</Th> */}
                  <Th>Index</Th>
                  <Th>User</Th>
                  <Th>Usage</Th>
                  {/* <Th>Expire</Th> */}
                  <Th display={{ sm: "None" }}>Enable</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {accounts.map((account, index) => (
                  <Tr key={account.id}>
                    <Td display={{ sm: "None" }}>{account.uuid} </Td>
                    {/* <Td>{account.email}</Td> */}
                    <Td>{index + 1 + curPage * rows}</Td>
                    <Td>
                      <HStack spacing={1}>
                        <User userId={account.user_id} />
                        <Tag
                          size="sm"
                          bgColor={account.enable ? "green.200" : "red.400"}
                          color={account.enable ? "black" : "white"}
                          borderRadius="full"
                        >
                          <TagLabel>{account.email}</TagLabel>
                        </Tag>
                      </HStack>
                    </Td>
                    <Td>
                      <Stack direction={"column"}>
                        <Badge
                          variant="solid"
                          colorScheme={
                            account.used_traffic_percent > 85 ? "red" : "green"
                          }
                        >
                          {niceBytes(account.used_traffic)} /{" "}
                          {niceBytes(account.data_limit)} (
                          {account.used_traffic_percent}%)
                        </Badge>

                        <Badge variant="solid" colorScheme="pink">
                          {account.expired_at
                            ? new Date(account.expired_at).toLocaleDateString(
                                "fa-IR-u-nu-latn"
                              )
                            : "Unlimited"}
                        </Badge>
                      </Stack>
                    </Td>
                    <Td display={{ sm: "None" }}>
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
                            icon={<EditIcon />}
                            onClick={() => {
                              setAccount(account);
                              onEditAccountOpen();
                            }}
                          >
                            Edit
                          </MenuItem>
                          <MenuItem
                            icon={<RepeatIcon />}
                            onClick={() => {
                              resetTraffic(account.id);
                            }}
                          >
                            Reset Traffic
                          </MenuItem>

                          <MenuItem
                            icon={<DeleteIcon />}
                            onClick={() => {
                              delteAccount(account.id);
                            }}
                          >
                            Delete
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

      <Box>
        <ReactPaginate
          activeClassName={"item active "}
          breakClassName={"item break-me "}
          breakLabel={"..."}
          containerClassName={"pagination"}
          disabledClassName={"disabled-page"}
          marginPagesDisplayed={2}
          nextClassName={"item next "}
          nextLabel={<ArrowRightIcon boxSize={5} />}
          onPageChange={handlePageClick}
          pageCount={total / rows}
          pageClassName={"item pagination-page "}
          pageRangeDisplayed={2}
          previousClassName={"item previous"}
          previousLabel={<ArrowLeftIcon boxSize={5} />}
        />
      </Box>
    </VStack>
  );
};

export default Accounts;
