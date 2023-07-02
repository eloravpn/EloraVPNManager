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
import HostModal from "../Hosts/components/HostModal";
import InboundForm from "./component/InboundForm";

const Inbounds = ({data}) => {

    const navigate = useNavigate();

    let location = useLocation();
    let actionData = useActionData();

    const [inbound, setInbound] = useState(null);


    const {isOpen, onOpen, onClose, getButtonProps} = useDisclosure();

    const {isOpen: isEditOpen, onOpen: onEditOpen, onClose: onEditClose} = useDisclosure()


    const cancelRef = React.useRef();

    const btnRef = React.useRef();

    return (
        <VStack spacing={4} p={5} align='stretch'>

             <InboundForm
                isOpen={isEditOpen}
                onClose={onEditClose}
                btnRef={btnRef}
                // inbound={host}
            />

            <Box>
                <Heading as='h3' size='lg'>
                    Inbounds
                </Heading>
            </Box>

            <Box>
                <Button leftIcon={<AddIcon/>} ref={btnRef} colorScheme='teal' onClick={() => {
                    // setHost(null);
                    onEditOpen();
                }}>
                    Create inbound
                </Button>
            </Box>

            <Box>
                {
                    data.length ? (
                            <TableContainer>
                                <Table variant='striped' colorScheme='teal'>
                                    <Thead>
                                        <Tr>
                                            <Th>Remark</Th>
                                            <Th>Host ID</Th>
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

                                                <Td>

                                                    {inbound.remark}
                                                </Td>
                                                <Td>
                                                    {inbound.host_id}
                                                </Td>
                                                <Td>
                                                    {inbound.domain}
                                                </Td>
                                                <Td>
                                                    {inbound.sni}
                                                </Td>
                                                <Td>
                                                    {inbound.type}
                                                </Td>
                                                <Td>
                                                    {inbound.develop ? <CheckCircleIcon color="green.400"/> :
                                                        <NotAllowedIcon/>}
                                                </Td>
                                                <Td>
                                                    {inbound.enable ? <CheckCircleIcon color="green.400"/> :
                                                        <NotAllowedIcon/>}
                                                </Td>

                                                <Td>
                                                    <Menu>
                                                        <MenuButton as={Button} rightIcon={<ChevronDownIcon/>}>
                                                            Actions
                                                        </MenuButton>
                                                    </Menu>
                                                </Td>

                                            </Tr>
                                        ))}


                                    </Tbody>
                                </Table>
                            </TableContainer>
                        ) :
                        (<div>
                            No Inbounds
                        </div>)
                }
            </Box>


        </VStack>

    );
};

export default Inbounds;
