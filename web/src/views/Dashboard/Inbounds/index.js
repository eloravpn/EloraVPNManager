import React, { useState } from "react";
import { Form } from "react-router-dom";
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
import InboundForm from "./component/InboundForm";

const Inbounds = ({ data }) => {
  const [inbound, setInbound] = useState(null);

  const { isOpen, onOpen, onClose } = useDisclosure();

  const {
    isOpen: isEditOpen,
    onOpen: onEditOpen,
    onClose: onEditClose,
  } = useDisclosure();

  const cancelRef = React.useRef();

  const btnRef = React.useRef();

  return (
    <VStack spacing={4} p={5} align="stretch">
      <InboundForm
        isOpen={isEditOpen}
        onClose={onEditClose}
        btnRef={btnRef}
        inbound={inbound}
      />

      <AlertDialog
        isOpen={isOpen}
        leastDestructiveRef={cancelRef}
        onClose={onClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete {inbound ? inbound.remark : ""}
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
                action={`inbound/${inbound ? inbound.id : 0}/destroy`}
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
          Inbounds
        </Heading>
      </Box>

      <Box>
        <Button
          leftIcon={<AddIcon />}
          ref={btnRef}
          colorScheme="teal"
          onClick={() => {
            setInbound(null);
            onEditOpen();
          }}
        >
          Create inbound
        </Button>
      </Box>

      <Box>
        {data.length ? (
          <TableContainer>
            <Table variant="striped" colorScheme="teal">
              <Thead>
                <Tr>
                  <Th>Remark</Th>
                  <Th>Host</Th>
                  <Th>Domain</Th>
                  <Th>SNI</Th>
                  <Th>Type</Th>
                  <Th>Enable</Th>
                  <Th>Develop</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data.map((inbound) => (
                  <Tr key={inbound.id}>
                    <Td>{inbound.remark}</Td>
                    <Td>{inbound.host.name}</Td>
                    <Td>{inbound.domain}</Td>
                    <Td>{inbound.sni}</Td>
                    <Td>{inbound.type}</Td>
                    <Td>
                      {inbound.develop ? (
                        <CheckCircleIcon color="green.400" />
                      ) : (
                        <NotAllowedIcon />
                      )}
                    </Td>
                    <Td>
                      {inbound.enable ? (
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
                              setInbound(inbound);
                              onOpen();
                            }}
                          >
                            Delete
                          </MenuItem>
                          <MenuItem
                            icon={<EditIcon />}
                            onClick={() => {
                              setInbound(inbound);
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
          <div>No Inbounds</div>
        )}
      </Box>
    </VStack>
  );
};

export default Inbounds;
