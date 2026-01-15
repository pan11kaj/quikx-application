import axios from "axios";
import react,{ useState } from "react";
import { Navigate, Outlet, useSearchParams } from "react-router-dom";


export const GuardRoute = ({Component})=>{
    const [auth,setAuth] = useState(false);
    const [searchParams] = useSearchParams()
    const fetchData = async () => {

      const printer_name = searchParams.get("printer_name")
      const url = process.env.REACT_APP_SERVER_NAME
      try {
        const response = await axios.post(url + "/printers/check-valid-printer", null, { params: { printer_name: printer_name } })
        if (response.status !== 404) {
          const isValid = response.data.valid

          return isValid;
        }
      } catch (err) {
        return false
      }
    }

    fetchData().then((data) => {
        setAuth(data);
    })

    return auth?<Component />:<Outlet/>

}