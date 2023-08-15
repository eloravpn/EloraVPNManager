import React, { useState } from "react";
import {
  Form,
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
  Badge,
  Box,
  Button,
  Heading,
  HStack,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Stack,
  Table,
  TableContainer,
  Tag,
  TagLabel,
  TagLeftIcon,
  Tbody,
  Td,
  Text,
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
  CopyIcon,
  DeleteIcon,
  EditIcon,
  LinkIcon,
  NotAllowedIcon,
  SettingsIcon,
} from "@chakra-ui/icons";
import InboundConfigForm from "./components/InboundConfigForm";
import { InboundConfigAPI } from "../../../api/InboundConfigAPI";

export const InboundConfigs = ({ data }) => {
  const navigate = useNavigate();

  let location = useLocation();
  let actionData = useActionData();

  const [inboundConfig, setInboundConfig] = useState(null);

  const { isOpen, onOpen, onClose, getButtonProps } = useDisclosure();

  const copyInboundConfig = (id) => {
    if (window.confirm("Are you sure to copy this inbound config?")) {
      InboundConfigAPI.copy(id).then(() => {
        navigate();
      });
    }
  };

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
      <InboundConfigForm
        isOpen={isEditOpen}
        onClose={onEditClose}
        btnRef={btnRef}
        inboundConfig={inboundConfig}
      />

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete {inboundConfig ? inboundConfig.remark : ""}
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
                action={`inbound-config/${
                  inboundConfig ? inboundConfig.id : 0
                }/destroy`}
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
          Inbound configs
        </Heading>
      </Box>
      <Box>
        <Button
          leftIcon={<AddIcon />}
          ref={btnRef}
          colorScheme="teal"
          onClick={() => {
            setInboundConfig(null);
            onEditOpen();
          }}
        >
          Create inbound config
        </Button>
      </Box>

      <Box>
        {data.length ? (
          <TableContainer>
            <Table variant="striped" colorScheme="teal">
              <Thead>
                <Tr>
                  <Th>Remark</Th>
                  <Th>Domain</Th>
                  <Th>Type</Th>
                  <Th>Enable</Th>
                  <Th>Develop</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data.map((inboundConfig) => (
                  <Tr key={inboundConfig.id}>
                    <Td>
                      <Stack direction={"column"}>
                        <Text as="b">{inboundConfig.remark}</Text>

                        <HStack spacing={4}>
                          <Tag p={1} size={5} colorScheme="blue">
                            <TagLeftIcon as={LinkIcon} />

                            <TagLabel>{inboundConfig.inbound.remark}</TagLabel>
                          </Tag>
                        </HStack>
                      </Stack>
                    </Td>
                    <Td>{inboundConfig.domain}</Td>
                    <Td>
                      <Stack direction="row">
                        <Badge colorScheme="green">{inboundConfig.type}</Badge>
                        <Badge colorScheme="blue">
                          {inboundConfig.network}
                        </Badge>
                        <Badge colorScheme="red">
                          {inboundConfig.finger_print}
                        </Badge>

                        <Badge colorScheme="orange">{inboundConfig.path}</Badge>
                      </Stack>
                    </Td>
                    <Td>
                      {inboundConfig.enable ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>
                    <Td>
                      {inboundConfig.develop ? (
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
                            icon={<CopyIcon />}
                            onClick={() => {
                              copyInboundConfig(inboundConfig.id);
                            }}
                          >
                            Copy
                          </MenuItem>
                          <MenuItem
                            icon={<DeleteIcon />}
                            onClick={() => {
                              setInboundConfig(inboundConfig);
                              onOpen();
                            }}
                          >
                            Delete
                          </MenuItem>
                          <MenuItem
                            icon={<EditIcon />}
                            onClick={() => {
                              setInboundConfig(inboundConfig);
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
          <div>No Inbound configs</div>
        )}
      </Box>
    </VStack>
  );
};
