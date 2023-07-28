import React, { useEffect } from "react";
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  HStack,
  Input,
  VStack,
  Text,
} from "@chakra-ui/react";
import { removeAuthToken, setAuthToken } from "../../../api/AuthStorage";
import { Form, useLocation, useNavigate } from "react-router-dom";
import { api, api_base } from "../../../api/axios";
// import {api} from "./axios";

const Login = () => {
  const navigate = useNavigate();

  let location = useLocation();

  useEffect(() => {
    removeAuthToken();
    if (location.pathname !== "/login") {
      navigate("/login", { replace: true });
    }
  }, []);
  const handleSubmit = (event) => {
    event.preventDefault();

    const formData = new FormData();
    formData.append("username", event.target.elements.username.value);
    formData.append("password", event.target.elements.password.value);
    formData.append("grant_type", "password");
    // setLoading(true);
    api_base
      .post("/admin/token", formData)
      .then((res) => {
        setAuthToken(res.data.access_token);
        navigate("/admin/dashboard");
      })
      .catch((err) => {
        console.log(err);
        // setError(err.response._data.detail);
      })
      .finally();
  };
  return (
    <VStack justifyContent="space-between" minH="100vh" p="6">
      <HStack w="full" justifyContent="center" alignItems="center">
        <Box w="full" maxW="340px" mt="6">
          <VStack alignItems="center" w="full">
            {/*<LogoIcon/>*/}
            <Text fontSize="2xl" fontWeight="semibold">
              Login to your account
            </Text>
            <Text color="gray.600" _dark={{ color: "gray.400" }}>
              Welcome back, please enter your details
            </Text>
          </VStack>

          <form onSubmit={handleSubmit}>
            <VStack mt={4} rowGap={4}>
              <FormControl>
                <FormLabel>Username</FormLabel>
                <Input w="full" placeholder="Username" name={"username"} />
              </FormControl>
              <FormControl>
                <FormLabel>Password</FormLabel>
                <Input
                  w="full"
                  type="password"
                  name={"password"}
                  placeholder="Password"
                />
              </FormControl>
              {/*{error && (*/}
              {/*  <Alert status="error" rounded="md">*/}
              {/*    <AlertIcon />*/}
              {/*    <AlertDescription>{error}</AlertDescription>*/}
              {/*  </Alert>*/}
              {/*)}*/}
              <Button
                // isLoading={loading}
                type="submit"
                w="full"
                colorScheme="primary"
              >
                Login
              </Button>
            </VStack>
          </form>
        </Box>
      </HStack>
    </VStack>
  );
};

export default Login;
