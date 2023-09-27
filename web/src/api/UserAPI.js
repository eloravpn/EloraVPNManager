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
    await api.request({
      url: `/users/${user.id}`,
      method: "PUT",
      data: user,
    });
  },
  deleteUser: async function (userId) {
    await api.request({
      url: `/users/${userId}`,
      method: "DELETE",
    });
  },
  getAll: async function (rows, sort) {
    let params = {
      limit: rows ? rows : 20,
      sort: sort ? sort : "-modified",
    };

    const response = await api.request({
      url: "/users/",
      method: "GET",
      params: params,
    });

    return response.data.users;
  },
};
