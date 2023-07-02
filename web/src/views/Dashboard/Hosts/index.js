import React, {useState} from 'react';
import {Form, Link, useActionData, useLocation, useNavigate} from "react-router-dom";
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
    DrawerCloseButton, DrawerContent,
    DrawerFooter,
    DrawerHeader,
    DrawerOverlay, Heading, Input,
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
    VStack
} from "@chakra-ui/react";
import {
    AddIcon,
    CheckCircleIcon,
    ChevronDownIcon,
    DeleteIcon,
    EditIcon,
    EmailIcon,
    NotAllowedIcon
} from "@chakra-ui/icons";
import HostModal from "./components/HostModal";


const Hosts = ({hosts}) => {

    const navigate = useNavigate();

    let location = useLocation();
    let actionData = useActionData();
    const [hostId, setHostId] = useState();

    const [host, setHost] = useState();

    const {isOpen, onOpen, onClose, getButtonProps} = useDisclosure();

    const {isOpen: isEditOpen, onOpen: onEditOpen, onClose: onEditClose} = useDisclosure()


    const buttonProps = getButtonProps()


    const cancelRef = React.useRef();

    const btnRef = React.useRef();

    return (


        <VStack spacing={4} p={5} align='stretch'>


            <HostModal
                isOpen={isEditOpen}
                onClose={onEditClose}
                btnRef={btnRef}
                host={host}
            />

            <AlertDialog
                isOpen={isOpen}
                leastDestructiveRef={cancelRef}
                onClose={onClose}
            >

                <AlertDialogOverlay>
                    <AlertDialogContent>
                        <AlertDialogHeader fontSize='lg' fontWeight='bold'>
                            Delete Customer
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
                                action={`host/${hostId}/destroy`}
                                onSubmit={onClose}
                            >
                                <Button colorScheme='red' type={'submit'} ml={3}>
                                    Delete
                                </Button>
                            </Form>


                        </AlertDialogFooter>
                    </AlertDialogContent>
                </AlertDialogOverlay>
            </AlertDialog>

            <Box>
                <Heading as='h3' size='lg'>
                    Hosts
                </Heading>
            </Box>


            <Box>

                {/*<Link to="new">*/}

                {/*    <Button leftIcon={<EmailIcon/>} colorScheme='teal' variant='solid'>*/}
                {/*        Create Host*/}
                {/*    </Button>*/}
                {/*</Link>*/}

                <Button leftIcon={<AddIcon/>} ref={btnRef} colorScheme='teal' onClick={() => {
                    setHost(null);
                    onEditOpen();
                }}>
                    Create host
                </Button>

                {/*<Outlet/>*/}

                {hosts.length ? (

                    <TableContainer>
                        <Table variant='striped' colorScheme='teal'>
                            <Thead>
                                <Tr>
                                    <Th>Name</Th>
                                    <Th>IP</Th>
                                    <Th>Domain</Th>
                                    <Th>Master</Th>
                                    <Th>Enable</Th>
                                    <Th>Actions</Th>
                                </Tr>
                            </Thead>
                            <Tbody>
                                {hosts.map((host) => (
                                    // <Link to={`hosts/${host.id}`}>

                                    <Tr key={host.id}>

                                        <Td>
                                            <Link to={`host/${host.id}`}>{host.name}</Link>

                                        </Td>
                                        <Td>
                                            {host.ip}
                                        </Td>
                                        <Td>
                                            {host.domain}

                                        </Td>
                                        <Td>
                                            {host.master ? <CheckCircleIcon color="green.400"/> : <NotAllowedIcon/>}
                                        </Td>
                                        <Td>
                                            {host.enable ? <CheckCircleIcon color="green.400"/> : <NotAllowedIcon/>}
                                        </Td>

                                        <Td>


                                            <Menu>
                                                <MenuButton as={Button} rightIcon={<ChevronDownIcon/>}>
                                                    Actions
                                                </MenuButton>
                                                <MenuList>
                                                    <MenuItem icon={<DeleteIcon/>} onClick={() => {
                                                        setHostId(host.id);
                                                        onOpen();

                                                    }
                                                    }>

                                                        Delete
                                                    </MenuItem>
                                                    <MenuItem icon={<EditIcon/>} onClick={() => {
                                                        // navigate(`host/${host.id}`)
                                                        setHost(host);
                                                        onEditOpen();
                                                    }
                                                    }>

                                                        Edit

                                                        {/*<Link to={}>Edit</Link>*/}
                                                    </MenuItem>
                                                    {/*<MenuItem>Mark as Draft</MenuItem>*/}
                                                    {/*<MenuItem>Delete</MenuItem>*/}
                                                    {/*<MenuItem>Attend a Workshop</MenuItem>*/}
                                                </MenuList>
                                            </Menu>
                                        </Td>
                                        {/*</Link>*/}
                                    </Tr>
                                ))}
                            </Tbody>

                        </Table>
                    </TableContainer>

                ) : (
                    <p>
                        <i>No hosts</i>
                    </p>
                )}
            </Box>


        </VStack>
    );
};

export default Hosts;
