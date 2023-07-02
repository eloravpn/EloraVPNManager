export const getAuthToken = () => {
  const token = localStorage.getItem("token");
  console.log('Token is ' + token);
  return token;
};

export const setAuthToken = (token) => {
  localStorage.setItem("token", token);
};

export const removeAuthToken = () => {
  console.log('Token removed.')
  localStorage.removeItem("token");
};
