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
  Box,
  Button,
  Heading,
  Menu,
  MenuButton,
  MenuItem,
  MenuList,
  Table,
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
  NotAllowedIcon,
  SettingsIcon,
} from "@chakra-ui/icons";
import InboundConfigForm from "./components/InboundConfigForm";

export const InboundConfigs = ({ data }) => {
  const navigate = useNavigate();

  let location = useLocation();
  let actionData = useActionData();

  const [inboundConfig, setInboundConfig] = useState(null);

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
                  <Th>Inbound</Th>
                  <Th>Domain</Th>
                  <Th>SNI</Th>
                  <Th>Type</Th>
                  <Th>Enable</Th>
                  <Th>Develop</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data.map((inboundConfig) => (
                  <Tr key={inboundConfig.id}>
                    <Td>{inboundConfig.remark}</Td>
                    <Td>{inboundConfig.inbound.remark}</Td>
                    <Td>{inboundConfig.domain}</Td>
                    <Td>{inboundConfig.sni}</Td>
                    <Td>{inboundConfig.type}</Td>
                    <Td>
                      {inboundConfig.develop ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>
                    <Td>
                      {inboundConfig.enable ? (
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
