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

const InboundForm = ({isOpen, onClose, btnRef, inbound}) => {

    const navigate = useNavigate();

    const [error, setError] = useState(false);
    const [hosts, setHosts] = useState(null);

    const validate = values => {
        const errors = {};

        if (!values.remark) {
            errors.name = 'Required';
        } else if (!values.host_id) {
            errors.host_id = 'Required';
        }

        return errors;
    };

    useEffect(() => {
        return () => {
            HostAPI.getAll().then((res) => {
                setHosts(res);
            })
        };
    }, []);


    const formik = useFormik({

        enableReinitialize: true,
        initialValues: {
            id: inbound ? inbound.id : 0,
            remark: inbound ? inbound.name : '',
            host_id: inbound ? inbound.host_id : '',

        }, validate, onSubmit: (values) => {

            setError(false);

            values.develop ? values.develop = true : values.develop = false;
            values.enable ? values.enable = true : values.enable = false;

            alert(JSON.stringify(values, null, 4));


            // if (values.id == 0) {
            //     HostAPI.createHost(values).then((res) => {
            //         // const toast = useToast()
            //         toast({
            //             title: 'Host created.',
            //             status: 'success',
            //             duration: 9000,
            //             isClosable: true,
            //         });
            //
            //         navigate('/admin/hosts');
            //
            //         onClose();
            //
            //         resetForm({values: ''})
            //
            //     }).catch(() => {
            //         setError(true);
            //     });
            // } else {
            //     HostAPI.updateHost(values).then((res) => {
            //         // const toast = useToast()
            //
            //         toast({
            //             title: 'Host updated.',
            //             status: 'success',
            //             duration: 9000,
            //             isClosable: true,
            //         });
            //
            //         navigate('/admin/hosts');
            //
            //         onClose();
            //
            //         resetForm({values: ''})
            //     }).catch(() => {
            //         setError(true);
            //     });
            // }
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
                <DrawerHeader>{!inbound ? 'Create inbound' : 'Edit inbound'}</DrawerHeader>

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

                        <Stack spacing={8} direction={['column', 'row']}>

                            <Box>
                                <FormControl isInvalid={formik.touched.remark && formik.errors.remark}>
                                    <FormLabel>Remark</FormLabel>
                                    <Input
                                        id={'remark'} name={'remark'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.remark}
                                        type='text'/>
                                    {formik.touched.remark && formik.errors.remark ? (
                                        <FormErrorMessage>{formik.errors.remark}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.remark && formik.errors.remark}>
                                    <FormLabel>Port</FormLabel>
                                    <Input
                                        id={'port'} name={'port'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.port}
                                        type='text'/>
                                    {formik.touched.port && formik.errors.port ? (
                                        <FormErrorMessage>{formik.errors.port}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.port && formik.errors.port}>
                                    <FormLabel>Port</FormLabel>
                                    <Input
                                        id={'port'} name={'port'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.port}
                                        type='text'/>
                                    {formik.touched.port && formik.errors.port ? (
                                        <FormErrorMessage>{formik.errors.port}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.domain && formik.errors.domain}>
                                    <FormLabel>Domain</FormLabel>
                                    <Input
                                        id={'domain'} name={'domain'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.domain}
                                        type='text'/>
                                    {formik.touched.domain && formik.errors.domain ? (
                                        <FormErrorMessage>{formik.errors.domain}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.request_host && formik.errors.request_host}>
                                    <FormLabel>Request Host</FormLabel>
                                    <Input
                                        id={'request_host'} name={'request_host'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.request_host}
                                        type='text'/>
                                    {formik.touched.request_host && formik.errors.request_host ? (
                                        <FormErrorMessage>{formik.errors.request_host}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.sni && formik.errors.sni}>
                                    <FormLabel>SNI</FormLabel>
                                    <Input
                                        id={'sni'} name={'sni'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.sni}
                                        type='text'/>
                                    {formik.touched.sni && formik.errors.sni ? (
                                        <FormErrorMessage>{formik.errors.sni}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.address && formik.errors.address}>
                                    <FormLabel>Address</FormLabel>
                                    <Input
                                        id={'address'} name={'address'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.address}
                                        type='text'/>
                                    {formik.touched.address && formik.errors.address ? (
                                        <FormErrorMessage>{formik.errors.address}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.path && formik.errors.path}>
                                    <FormLabel>Path</FormLabel>
                                    <Input
                                        id={'address'} name={'address'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.path}
                                        type='text'/>
                                    {formik.touched.path && formik.errors.path ? (
                                        <FormErrorMessage>{formik.errors.path}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>

                            <Box>
                                <FormControl isInvalid={formik.touched.path && formik.errors.path}>
                                    <FormLabel>Path</FormLabel>
                                    <Input
                                        id={'address'} name={'address'}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        value={formik.values.path}
                                        type='text'/>
                                    {formik.touched.path && formik.errors.path ? (
                                        <FormErrorMessage>{formik.errors.path}</FormErrorMessage>) : null}
                                </FormControl>
                            </Box>


                             <Stack spacing={5} direction='row'>


                                <FormLabel htmlFor='enable' mb='0'>
                                    Enable?
                                </FormLabel>
                                <Switch defaultChecked={(inbound && inbound.enable || !inbound) ? true : false}
                                        onChange={formik.handleChange}
                                        onBlur={formik.handleBlur}
                                        name={'enable'} id='enable'
                                        value={formik.values.enable}
                                />

                                <FormLabel htmlFor='master' mb='0'>
                                    Develop?
                                </FormLabel>
                                <Switch
                                    defaultChecked={inbound && inbound.develop ? true : false}
                                    onChange={formik.handleChange}
                                    onBlur={formik.handleBlur}
                                    name={'develop'} id='develop'
                                    value={formik.values.develop}
                                />
                            </Stack>

                            <Select name={'host_id'}
                                    onChange={formik.handleChange}
                                    onBlur={formik.handleBlur}
                                    value={formik.values.host_id}
                                    placeholder='Select Host'>

                                {
                                    hosts ? hosts.map((host) => (
                                            <option value={host.id}>
                                                {host.name}
                                            </option>
                                        )
                                    ) : ('')
                                }

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
        </Drawer>
    );
};

export default InboundForm;
