import {
    Alert, AlertIcon,
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
    FormErrorMessage,
    FormLabel,
    Input,
    Select,
    Stack,
    Switch
} from "@chakra-ui/react";
import React, {useEffect, useState} from "react";
import {useFormik} from 'formik';
import {HostAPI} from "../../../../api/HostAPI";
import {toast} from "../../../../index";
import {useNavigate} from "react-router-dom";


const HostModal = ({isOpen, onClose, btnRef, host}) => {

    const navigate = useNavigate();

    const [error, setError] = useState(false);

    const validate = values => {
        const errors = {};

        if (!values.name) {
            errors.name = 'Required';
        }

        return errors;
    };

    const formik = useFormik({

        enableReinitialize: true,
        initialValues: {
            id: host ? host.id : 0,
            name: host ? host.name : '',
            domain: host ? host.domain : '',
            ip: host ? host.ip : '',
            port: host ? host.port : '',
            username: host ? host.username : '',
            password: host ? host.password : '',
            api_path: host ? host.api_path : '',
            enable: host ? host.enable : true,
            master: host ? host.master : '',
            type: host ? host.type : 'X-UI-MHSANAEI',
        }, validate, onSubmit: (values, {resetForm}) => {

            setError(false);

            values.master ? values.master = true : values.master = false;
            values.enable ? values.enable = true : values.enable = false;


            if (values.id == 0) {
                HostAPI.createHost(values).then((res) => {
                    // const toast = useToast()
                    toast({
                        title: 'Host created.',
                        status: 'success',
                        duration: 9000,
                        isClosable: true,
                    });

                    navigate('/admin/hosts');

                    onClose();

                    resetForm({values: ''})

                }).catch(() => {
                    setError(true);
                });
            } else {
                HostAPI.updateHost(values).then((res) => {
                    // const toast = useToast()

                    toast({
                        title: 'Host updated.',
                        status: 'success',
                        duration: 9000,
                        isClosable: true,
                    });

                    navigate('/admin/hosts');

                    onClose();

                    resetForm({values: ''})
                }).catch(() => {
                    setError(true);
                });
            }
        },
    });


    return (
        <Drawer
            size={'lg'}
            isOpen={isOpen}
            placement='right'
            onClose={onClose}
            finalFocusRef={btnRef}
        >
            <DrawerOverlay/>
            <DrawerContent>
                <DrawerCloseButton/>
                <DrawerHeader>{!host ? 'Create host' : 'Edit host'}</DrawerHeader>

                <DrawerBody>
                    <form id={"fm1"} onSubmit={formik.handleSubmit}>

                        {error ? (<Alert status='error'>
                            <AlertIcon/>
                            There was an error processing your request
                        </Alert>) : ''}

                        <Input id={'id'} name={'id'} type={"hidden"}
                               onChange={formik.handleChange}
                               onBlur={formik.handleBlur}
                               value={formik.values.id}/>

                        <Stack spacing={8} direction={['column', 'column']}>

                            <Box width='full' >
                                <FormControl isInvalid={formik.touched.name && formik.errors.name}>
                                    <FormLabel>Name</FormLabel>
                                    <Input
                                        id={'name'} name={'name'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.name}
                                        type='text'/>
                                    {formik.touched.name && formik.errors.name ? (
                                        <FormErrorMessage>{formik.errors.name}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormLabel>Domain</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.domain : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.domain}
                                       name={'domain'}
                                       type='text'/>
                            </Box>

                            <Box>
                                <FormLabel>IP</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.ip : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.ip}
                                       name={'ip'} type='text'/>
                            </Box>

                            <Box>
                                <FormLabel>Port</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.port : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.port}
                                       name={'port'}
                                       type='number'/>
                            </Box>

                            <Box>
                                <FormLabel>User Name</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.username : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.username}
                                       name={'username'}
                                       type='text'/>
                            </Box>


                            <Box>
                                <FormLabel>Password</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.password : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.password}
                                       name={'password'}
                                       type='text'/>
                            </Box>
                            <Box>
                                <FormLabel>API Path</FormLabel>
                                <Input isRequired={true}
                                    // defaultValue={host ? host.api_path : ''}
                                       onChange={formik.handleChange}
                                       onBlur={formik.handleBlur}
                                       value={formik.values.api_path}
                                       name={'api_path'}
                                       type='text'/>
                            </Box>


                            <Stack spacing={5} direction='row'>


                                <FormLabel htmlFor='enable' mb='0'>
                                    Enable?
                                </FormLabel>
                                <Switch defaultChecked={(host && host.enable || !host) ? true : false}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        name={'enable'} id='enable'
                                        value={formik.values.enable}
                                />

                                <FormLabel htmlFor='master' mb='0'>
                                    Master?
                                </FormLabel>
                                <Switch
                                    defaultChecked={host && host.master ? true : false}
                                    onChange={formik.handleChange}
                                    onBlur={formik.handleBlur}
                                    name={'master'} id='master'
                                    value={formik.values.master}
                                />
                            </Stack>


                            <Select name={'type'}
                                    onChange={formik.handleChange}
                                    onBlur={formik.handleBlur}
                                    value={formik.values.type}
                                    placeholder='Select Type'>

                                <option value='X-UI-MHSANAEI'>X-UI SAnaei</option>
                            </Select>


                        </Stack>


                    </form>
                </DrawerBody>

                <DrawerFooter>
                    <Button variant='outline' mr={3} onClick={onClose}>
                        Cancel
                    </Button>
                    <Button colorScheme='blue' type={"submit"} form={"fm1"}>Save</Button>
                </DrawerFooter>
            </DrawerContent>
        </Drawer>)
}


export default HostModal;
