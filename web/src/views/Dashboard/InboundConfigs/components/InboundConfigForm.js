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
import React, { useEffect, useState } from "react";
import { useFormik } from "formik";
import { HostAPI } from "../../../../api/HostAPI";
import { toast } from "../../../../index";
import { useNavigate } from "react-router-dom";
import { InboundAPI } from "../../../../api/InboundAPI";
import { InboundConfigAPI } from "api/InboundConfigAPI";

const InboundConfigForm = ({ isOpen, onClose, btnRef, inboundConfig }) => {
  const navigate = useNavigate();

  const [error, setError] = useState(false);
  const [inbounds, setInbounds] = useState(null);

  const validate = (values) => {
    const errors = {};

    if (!values.remark) {
      errors.remark = "Required";
    } else if (!values.inbound_id) {
      errors.inbound_id = "Required";
    }

    return errors;
  };

  useEffect(() => {
    InboundAPI.getAll().then((res) => {
      setInbounds(res);
    });
  }, []);

  const formik = useFormik({
    enableReinitialize: true,
    initialValues: {
      id: inboundConfig ? inboundConfig.id : 0,
      remark: inboundConfig ? inboundConfig.remark : "",
      inbound_id: inboundConfig ? inboundConfig.inbound_id : "",
      port: inboundConfig ? inboundConfig.port : "",
      domain: inboundConfig ? inboundConfig.domain : "",
      host: inboundConfig ? inboundConfig.host : "",
      sni: inboundConfig ? inboundConfig.sni : "",
      address: inboundConfig ? inboundConfig.address : "",
      path: inboundConfig ? inboundConfig.path : "",
      enable: inboundConfig ? inboundConfig.enable : true,
      develop: inboundConfig ? inboundConfig.develop : "",
      type: inboundConfig ? inboundConfig.type : "vless",
      finger_print: inboundConfig ? inboundConfig.finger_print : "none",
      security: inboundConfig ? inboundConfig.security : "tls",
    },
    validate,
    onSubmit: (values) => {
      setError(false);

      values.develop ? (values.develop = true) : (values.develop = false);
      values.enable ? (values.enable = true) : (values.enable = false);

      // alert(JSON.stringify(values, null, 4));

      if (values.id === 0) {
        InboundConfigAPI.create(values)
          .then((res) => {
            // const toast = useToast()
            toast({
              title: "Inbound config created.",
              status: "success",
              duration: 9000,
              isClosable: true,
            });

            navigate("/admin/inbound-configs");

            onClose();
          })
          .catch(() => {
            setError(true);
          });
      } else {
        InboundConfigAPI.update(values)
          .then((res) => {
            // const toast = useToast()

            toast({
              title: "Inbound config updated.",
              status: "success",
              duration: 9000,
              isClosable: true,
            });

            navigate("/admin/inbound-configs");

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
        <DrawerHeader>
          {!inboundConfig ? "Create inbound config" : "Edit inbound config"}
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

            <Stack spacing={4} direction={["column", "column"]}>
              <Box>
                <FormControl
                  isInvalid={formik.touched.remark && formik.errors.remark}
                >
                  <FormLabel>Remark</FormLabel>
                  <Input
                    id={"remark"}
                    name={"remark"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    defaultValue={formik.values.remark}
                    type="text"
                  />
                  {formik.touched.remark && formik.errors.remark ? (
                    <FormErrorMessage>{formik.errors.remark}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.port && formik.errors.port}
                >
                  <FormLabel>Port</FormLabel>
                  <Input
                    id={"port"}
                    name={"port"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.port}
                    type="text"
                  />
                  {formik.touched.port && formik.errors.port ? (
                    <FormErrorMessage>{formik.errors.port}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.domain && formik.errors.domain}
                >
                  <FormLabel>Domain</FormLabel>
                  <Input
                    id={"domain"}
                    name={"domain"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.domain}
                    type="text"
                  />
                  {formik.touched.domain && formik.errors.domain ? (
                    <FormErrorMessage>{formik.errors.domain}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.host && formik.errors.host}
                >
                  <FormLabel>Request Host</FormLabel>
                  <Input
                    id={"host"}
                    name={"host"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.host}
                    type="text"
                  />
                  {formik.touched.host && formik.errors.host ? (
                    <FormErrorMessage>{formik.errors.host}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.sni && formik.errors.sni}
                >
                  <FormLabel>SNI</FormLabel>
                  <Input
                    id={"sni"}
                    name={"sni"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.sni}
                    type="text"
                  />
                  {formik.touched.sni && formik.errors.sni ? (
                    <FormErrorMessage>{formik.errors.sni}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.address && formik.errors.address}
                >
                  <FormLabel>Address</FormLabel>
                  <Input
                    id={"address"}
                    name={"address"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.address}
                    type="text"
                  />
                  {formik.touched.address && formik.errors.address ? (
                    <FormErrorMessage>{formik.errors.address}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormControl
                  isInvalid={formik.touched.path && formik.errors.path}
                >
                  <FormLabel>Path</FormLabel>
                  <Input
                    id={"path"}
                    name={"path"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.path}
                    type="text"
                  />
                  {formik.touched.path && formik.errors.path ? (
                    <FormErrorMessage>{formik.errors.path}</FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Box>
                <FormLabel>Security</FormLabel>

                <Select
                  name={"security"}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.security}
                  placeholder="Select Security"
                >
                  <option value="tls">TLS</option>
                  <option value="none">None</option>
                </Select>
              </Box>

              <Box>
                <FormLabel>Finger Print</FormLabel>
                <Select
                  name={"finger_print"}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.finger_print}
                  placeholder="Select Finger Print"
                >
                  <option value="none">None</option>
                  <option value="chrome">Chrome</option>
                  <option value="firefox">Firefox</option>
                </Select>
              </Box>

              <Box>
                <FormLabel>Type</FormLabel>

                <Select
                  name={"type"}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  value={formik.values.type}
                  placeholder="Select Type"
                >
                  <option value="vless">VLESS</option>
                  <option value="vmess">VMESS</option>
                  <option value="trojan">Trojan</option>
                  <option value="shadowsocks">Shadowsocks</option>
                </Select>
              </Box>

              <Box>
                <FormLabel>Type</FormLabel>

                <FormControl
                  isInvalid={
                    formik.touched.inbound_id && formik.errors.inbound_id
                  }
                >
                  <Select
                    name={"inbound_id"}
                    onChange={formik.handleChange}
                    onBlur={formik.handleBlur}
                    value={formik.values.inbound_id}
                    placeholder="Select Inbound"
                  >
                    {inbounds
                      ? inbounds.map((inbound) => (
                        <option value={inbound.id}>{inbound.remark}</option>
                      ))
                      : ""}
                  </Select>

                  {formik.touched.inbound_id && formik.errors.inbound_id ? (
                    <FormErrorMessage>
                      {formik.errors.inbound_id}
                    </FormErrorMessage>
                  ) : null}
                </FormControl>
              </Box>

              <Stack spacing={5} direction="row">
                <FormLabel htmlFor="enable" mb="0">
                  Enable?
                </FormLabel>
                <Switch
                  defaultChecked={
                    (inboundConfig && inboundConfig.enable) || !inboundConfig
                      ? true
                      : false
                  }
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  name={"enable"}
                  id="enable"
                  value={formik.values.enable}
                />

                <FormLabel htmlFor="master" mb="0">
                  Develop?
                </FormLabel>
                <Switch
                  defaultChecked={
                    inboundConfig && inboundConfig.develop ? true : false
                  }
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  name={"develop"}
                  id="develop"
                  value={formik.values.develop}
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

export default InboundConfigForm;
