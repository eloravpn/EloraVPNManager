import React from "react";
import { api } from "./axios";
import login from "../views/Dashboard/Login";
import { getAuthToken } from "./AuthStorage";
import axios from "axios";

export const AccountAPI = {
  get: async function (accountId) {
    const response = await api.request({
      url: `/accounts/${accountId}`,
      method: "GET",
    });

    return response.data;
  },
  create: async function (account) {
    await api.request({
      url: `/accounts/`,
      method: "POST",
      data: account,
    });
  },
  update: async function (account) {
    await api.request({
      url: `/accounts/${account.id}`,
      method: "PUT",
      data: account,
    });
  },
  delete: async function (accountId) {
    await api.request({
      url: `/accounts/${accountId}`,
      method: "DELETE",
    });
  },
  reseteTraffic: async function (accountId) {
    await api.request({
      url: `/accounts/${accountId}/reset_traffic`,
      method: "POST",
    });
  },
  getAll: async function () {
    let params = {
      limit: 10,
      sort: '-expire'
    };

    const response = await api.request({
      url: "/accounts/",
      method: "GET",
      params: params
    });

    return response.data.accounts;
  },
};
