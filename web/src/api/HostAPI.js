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

    let params = {
      limit: 20,
      sort: "-domain",
      enable: -1, // -1:All, 0:Enabled, 1:Disabled
      offset: 0,
      q: "",
    };

    const response = await api.request({
      url: "/hosts/",
      method: "GET",
      params: params,
    });

    return response.data.hosts;
  },
};
