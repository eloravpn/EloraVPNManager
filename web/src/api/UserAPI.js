import React from "react";
import { api } from "./axios";
import login from "../views/Dashboard/Login";
import { getAuthToken } from "./AuthStorage";
import axios from "axios";

export const UserAPI = {
  get: async function (userId) {
    const response = await api.request({
      url: `/users/${userId}`,
      method: "GET",
    });

    return response.data;
  },
  createUser: async function (user) {
    await api.request({
      url: `/users/`,
      method: "POST",
      data: user,
    });
  },
  updateUser: async function (user) {
    console.log("User Update :", user);
    await api.request({
      url: `/users/${user.id}`,
      method: "PUT",
      data: user,
    });
  },
  deleteUser: async function (userId) {
    console.log("User delete :", userId);
    await api.request({
      url: `/users/${userId}`,
      method: "DELETE",
    });
  },
  getAll: async function () {
    const response = await api.request({
      url: "/users/",
      method: "GET",
    });

    console.log(response.data.users);
    return response.data.users;
  },
};
