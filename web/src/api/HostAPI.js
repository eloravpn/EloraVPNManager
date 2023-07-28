import React from "react";
import { api } from "./axios";
import login from "../views/Dashboard/Login";
import { getAuthToken } from "./AuthStorage";
import axios from "axios";

export const HostAPI = {
  get: async function (hostId) {
    const response = await api.request({
      url: `/hosts/${hostId}`,
      method: "GET",
    });

    return response.data;
  },
  createHost: async function (host) {
    await api.request({
      url: `/hosts/`,
      method: "POST",
      data: host,
    });
  },
  updateHost: async function (host) {
    await api.request({
      url: `/hosts/${host.id}`,
      method: "PUT",
      data: host,
    });
  },
  deleteHost: async function (hostId) {
    await api.request({
      url: `/hosts/${hostId}`,
      method: "DELETE",
    });
  },
  getAll: async function () {
    const response = await api.request({
      url: "/hosts/",
      method: "GET",
    });

    return response.data.hosts;
  },
};
