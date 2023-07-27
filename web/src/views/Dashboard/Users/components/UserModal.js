import {
  Alert,
  AlertIcon,
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
  Switch,
} from "@chakra-ui/react";
import { useFormik } from "formik";
import { useState } from "react";
import { HostAPI } from "../../../../api/HostAPI";
import { toast } from "../../../../index";

import { useNavigate } from "react-router-dom";
import { UserAPI } from "../../../../api/UserAPI";
const UserModal = ({ isOpen, onClose, btnRef, user }) => {
  const navigate = useNavigate();

  const [error, setError] = useState(false);

  const validate = (values) => {
    const errors = {};

    if (!values.username) {
      errors.username = "Required";
    }

    return errors;
  };

  const formik = useFormik({
    enableReinitialize: true,
    initialValues: {
      id: user ? user.id : 0,
      username: user ? user.username : "",
      first_name: user ? user.first_name : "",
      last_name: user ? user.last_name : "",
      description: user ? user.description : "",
      telegram_chat_id: user ? user.telegram_chat_id : "",
      telegram_username: user ? user.telegram_username : "",
      phone_number: user ? user.phone_number : "",
      password: user ? user.password : "",
      enable: user ? user.enable : true,
      banned: user ? user.banned : false,
    },
    validate,
    onSubmit: (values) => {
      setError(false);

      values.enable ? (values.enable = true) : (values.enable = false);
      values.banned ? (values.banned = true) : (values.banned = false);
      if (!values.telegram_chat_id) delete values.telegram_chat_id;
      if (!values.phone_number) delete values.phone_number;
      if (!values.telegram_username) delete values.telegram_username;

      alert(JSON.stringify(values, null, 4));

      if (values.id === 0) {
        UserAPI.createUser(values)
          .then((res) => {
            // const toast = useToast()
            toast({
              title: "User created.",
              status: "success",
              duration: 9000,
              isClosable: true,
            });

            navigate("/admin/users");

            onClose();
          })
          .catch(() => {
            setError(true);
          });
      } else {
        UserAPI.updateUser(values)
          .then((res) => {
            // const toast = useToast()

            toast({
              title: "User updated.",
              status: "success",
              duration: 9000,
              isClosable: true,
            });

            navigate("/admin/users");

            onClose();
          })
          .catch(() => {
            setError(true);
          });
      }
    },
  });

  return (
    <Drawer
      size={"lg"}
      isOpen={isOpen}
      placement="right"
      onClose={onClose}
      finalFocusRef={btnRef}
    >
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>{!user ? "Create user" : "Edit user"}</DrawerHeader>

        <DrawerBody>
          <form id={"fm1"} onSubmit={formik.handleSubmit}>
            {error ? (
              <Alert status="error">
                <AlertIcon />
                There was an error processing your request
              </Alert>
            ) : (
              ""
            )}

            <Input
              id={"id"}
              name={"id"}
              type={"hidden"}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.id}
            />

            <Stack spacing={4} direction={["column", "column"]}>
              <Box>
                <FormControl
                  isInvalid={
                    formik.touched.first_name && formik.errors.first_name
                  }
                >
                  <FormLabel>First Name</FormLabel>
                  <Input
                    id={"first_name"}
                    name={"first_name"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.first_name}
                    type="text"
                  />
                  {formik.touched.first_name && formik.errors.first_name ? (
                    <FormErrorMessage>
                      {formik.errors.first_name}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={
                    formik.touched.last_name && formik.errors.last_name
                  }
                >
                  <FormLabel>Last Name</FormLabel>
                  <Input
                    id={"last_name"}
                    name={"last_name"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.last_name}
                    type="text"
                  />
                  {formik.touched.last_name && formik.errors.last_name ? (
                    <FormErrorMessage>
                      {formik.errors.last_name}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={formik.touched.username && formik.errors.username}
                >
                  <FormLabel>Username</FormLabel>
                  <Input
                    id={"username"}
                    name={"username"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.username}
                    type="text"
                  />
                  {formik.touched.username && formik.errors.username ? (
                    <FormErrorMessage>
                      {formik.errors.username}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={formik.touched.password && formik.errors.password}
                >
                  <FormLabel>Password</FormLabel>
                  <Input
                    disabled={user}
                    id={"password"}
                    name={"password"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.password}
                    type="text"
                  />
                  {formik.touched.password && formik.errors.password ? (
                    <FormErrorMessage>
                      {formik.errors.password}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={
                    formik.touched.telegram_chat_id &&
                    formik.errors.telegram_chat_id
                  }
                >
                  <FormLabel>Telegram Chat ID</FormLabel>
                  <Input
                    id={"telegram_chat_id"}
                    name={"telegram_chat_id"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.telegram_chat_id}
                    type="text"
                  />
                  {formik.touched.telegram_chat_id &&
                  formik.errors.telegram_chat_id ? (
                    <FormErrorMessage>
                      {formik.errors.telegram_chat_id}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={
                    formik.touched.telegram_username &&
                    formik.errors.telegram_username
                  }
                >
                  <FormLabel>Telegram Username</FormLabel>
                  <Input
                    id={"telegram_username"}
                    name={"telegram_username"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.telegram_username}
                    type="text"
                  />
                  {formik.touched.telegram_username &&
                  formik.errors.telegram_username ? (
                    <FormErrorMessage>
                      {formik.errors.telegram_username}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>
              <Box>
                <FormControl
                  isInvalid={
                    formik.touched.phone_number && formik.errors.phone_number
                  }
                >
                  <FormLabel>Phone Number</FormLabel>
                  <Input
                    id={"phone_number"}
                    name={"phone_number"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.phone_number}
                    type="text"
                  />
                  {formik.touched.phone_number && formik.errors.phone_number ? (
                    <FormErrorMessage>
                      {formik.errors.phone_number}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Stack spacing={5} direction="row">
                <FormLabel htmlFor="enable" mb="0">
                  Enable?
                </FormLabel>
                <Switch
                  defaultChecked={formik.values.enable}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  name={"enable"}
                  id="enable"
                  value={formik.values.enable}
                />

                <FormLabel htmlFor="banned" mb="0">
                  Banned?
                </FormLabel>
                <Switch
                  defaultChecked={formik.values.banned}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  name={"banned"}
                  id="banned"
                  value={formik.values.banned}
                />
              </Stack>
            </Stack>
          </form>
        </DrawerBody>

        <DrawerFooter>
          <Button variant="outline" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" type={"submit"} form={"fm1"}>
            Save
          </Button>
        </DrawerFooter>
      </DrawerContent>
    </Drawer>
  );
};

export default UserModal;
