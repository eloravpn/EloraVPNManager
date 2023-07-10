import {
  Alert,
  AlertIcon,
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
  Flex,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Input,
  NumberDecrementStepper,
  NumberIncrementStepper,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  Radio,
  RadioGroup,
  Select,
  Slider,
  SliderFilledTrack,
  SliderThumb,
  SliderTrack,
  Stack,
  Switch,
} from "@chakra-ui/react";
import { useField, useFormik, useFormikContext } from "formik";
import React, { useEffect, useMemo, useState } from "react";
import { HostAPI } from "../../../../api/HostAPI";
import { toast } from "../../../../index";

import { useNavigate } from "react-router-dom";
import { UserAPI } from "../../../../api/UserAPI";
import { AccountAPI } from "../../../../api/AccountAPI";
const AccountModal = ({ isOpen, onClose, btnRef, user, account }) => {
  const navigate = useNavigate();

  const [error, setError] = useState(false);
  const [uuid, setUUID] = useState();
  const [email, setemail] = useState();
  const [expiredAt, setexpiredAt] = useState();
  const [jalaliExpiredAt, setjalaliExpiredAt] = useState(null);
  // const [daysExpired, setdaysExpired] = useState();

  // const [value, setValue] = React.useState(0);

  const handleChange = (value) => {
    formik.setFieldValue("data_limit", value);
  };

  const handleChangeDaysExpired = (value) => {
    let numberOfMlSeconds = new Date().getTime();
    let addMlSeconds = 24 * value * 60 * 60 * 1000;
    let newDateObj = new Date(numberOfMlSeconds + addMlSeconds);

    setexpiredAt(newDateObj.toString());
    formik.setFieldValue("expired_at", newDateObj.toISOString());
  };


  const validate = (values) => {
    const errors = {};

    if (!values.uuid) {
      errors.uuid = "Required";
    } else if (!values.email) {
      errors.email = "Required";
    }

    return errors;
  };

  const uuidGenerator = () => {
    return ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, (c) =>
      (
        c ^
        (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))
      ).toString(16)
    );
  };

  const emailGenerator = () => {
    return Math.random().toString(36).slice(2, 8);
  };



  useEffect(() => {
    if (!account) {
      setUUID(uuidGenerator);
      setemail(emailGenerator);
      setexpiredAt(null);
    } else {
      setexpiredAt(account.expired_at);
    }
  }, [isOpen]);

  useEffect(() => {
    let date = new Date(expiredAt);
    let options = { year: "numeric", month: "long", day: "numeric" };
    let expiredAtJalali = date.toLocaleDateString("fa-IR-u-nu-latn");
    setjalaliExpiredAt(expiredAt ? expiredAtJalali : null);
  }, [expiredAt]);

  useEffect(() => {
    formik.setFieldValue("uuid", uuid);
    formik.setFieldValue("email", email);
  }, [uuid, email]);

  useEffect(() => {
    formik.setFieldValue("user_id", user ? user.id : 0);
  }, [user]);

  const formik = useFormik({
    enableReinitialize: true,
    initialValues: {
      id: account ? account.id : 0,
      uuid: account ? account.uuid : "",
      email: account ? account.email : "",
      data_limit: account ? account.data_limit : 20,
      expired_at: account ? account.expired_at : "",
      days_expired: 0,
      user_id: 0,
      enable: account ? account.enable : true,
    },
    validate,
    onSubmit: (values) => {
      setError(false);

      // if (!account) {
      //   setFieldValue("uuid", uuid);
      // }
      values.enable ? (values.enable = true) : (values.enable = false);
      console.log(values);
      alert(JSON.stringify(values, null, 4));

      if (values.id === 0) {
        AccountAPI.create(values)
          .then((res) => {
            // const toast = useToast()
            toast({
              title: "Account created.",
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
        AccountAPI.update(values)
          .then((res) => {
            // const toast = useToast()

            toast({
              title: "Account updated.",
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

  // useEffect(() => {
  //   formik.setFieldValue("data_limit", value);
  // }, [value]);

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
        <DrawerHeader>
          {account
            ? "Update account " + account.uuid + " " + account.enable
            : "Add new account for: "}
          {user ? user.first_name + " " + user.last_name : ""}
        </DrawerHeader>

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
            <Input
              id={"data_limit"}
              name={"data_limit"}
              type={"hidden"}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.data_limit}
            />

            <Input
              id={"user_id"}
              name={"user_id"}
              type={"hidden"}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.user_id}
            />

            <Input
              id={"expired_at"}
              name={"expired_at"}
              type={"hidden"}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
              value={formik.values.expired_at}
            />

            <Stack spacing={4} direction={["column", "column"]}>
              <Box>
                <FormControl
                  isInvalid={formik.touched.uuid && formik.errors.uuid}
                >
                  <FormLabel>UUID</FormLabel>
                  <Input
                    id={"uuid"}
                    name={"uuid"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.initialValues.uuid || uuid}
                    type="text"
                  />
                  {formik.touched.uuid && formik.errors.uuid ? (
                    <FormErrorMessage>{formik.errors.uuid}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.email && formik.errors.email}
                >
                  <FormLabel>Email</FormLabel>
                  <Input
                    id={"email"}
                    name={"email"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.initialValues.email || email}
                    type="text"
                  />
                  {formik.touched.email && formik.errors.email ? (
                    <FormErrorMessage>{formik.errors.email}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              {/* <Box>
                <FormControl
                  isInvalid={
                    formik.touched.data_limit && formik.errors.data_limit
                  }
                >
                  <FormLabel>Data Limit (GB)</FormLabel>
                  <Input
                    id={"data_limit"}
                    name={"data_limit"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.data_limit}
                    type="number"
                  />
                  {formik.touched.data_limit && formik.errors.data_limit ? (
                    <FormErrorMessage>
                      {formik.errors.data_limit}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box> */}

              <Box>
                <Flex>
                  <NumberInput
                    maxW="100px"
                    mr="2rem"
                    value={formik.values.data_limit}
                    onChange={handleChange}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Slider
                    max={500}
                    flex="1"
                    focusThumbOnChange={false}
                    value={formik.values.data_limit}
                    onChange={handleChange}
                  >
                    <SliderTrack>
                      <SliderFilledTrack />
                    </SliderTrack>
                    <SliderThumb
                      fontSize="sm"
                      boxSize="32px"
                      children={formik.values.data_limit}
                    />
                  </Slider>
                </Flex>
              </Box>

              <Box>
                <Badge variant="outline" colorScheme="green">
                  {jalaliExpiredAt
                    ? "Expired At: " + jalaliExpiredAt
                    : "Unlimited"}
                </Badge>
                <FormControl
                  isInvalid={
                    formik.touched.days_expired && formik.errors.days_expired
                  }
                >
                  <FormLabel>Expire Days</FormLabel>
                  <RadioGroup
                    onChange={handleChangeDaysExpired}
                    defaultValue={formik.values.days_expired}
                  >
                    <Stack direction="row" spacing={4}>
                      {/* <Radio value="0">Unlimited</Radio> */}
                      <Radio value="1">1 D</Radio>
                      <Radio value="3">3 D</Radio>
                      <Radio value="7">1 W</Radio>
                      <Radio value="30">1 M</Radio>
                      <Radio value="60">2 M</Radio>
                      <Radio value="90">3 M</Radio>
                      <Radio value="180">6 M</Radio>
                    </Stack>
                  </RadioGroup>

                  {formik.touched.days_expired && formik.errors.days_expired ? (
                    <FormErrorMessage>
                      {formik.errors.days_expired}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Stack spacing={5} direction="row">
                <FormLabel htmlFor="enable" mb="0">
                  Enable?
                </FormLabel>
                <Switch
                  isChecked={formik.values.enable}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  name={"enable"}
                  id={"enable"}
                  value={formik.values.enable}
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

export default AccountModal;
