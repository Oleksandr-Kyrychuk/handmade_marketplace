import { useMutation } from "@tanstack/react-query"
import { LogInRequestDTO } from "../../../../entities/auth/model/types/interfaces"
import { toast } from "react-toastify";
import { authService } from "@/entities/auth/model";

function useLogInMutation() {

  const {mutate: mutateLogIn, isPending: mutateLoginPending, isError, error} = useMutation({
    mutationFn: (data: LogInRequestDTO) => authService.logInAuth(data),
    onSuccess: (data) => {
      toast.success('You have successfully logged in')
      console.log('Log in success')
      console.log('Log in success', data)
      if(data?.success) {
        console.log('data.access', data)
      }
    },
    onError: (error) => {
      console.log('useLogInMutation error: ', error)
    },
  })

  return {mutateLogIn, mutateLoginPending, isError, error}
}

export default useLogInMutation;