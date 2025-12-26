import { authService } from "@/entities/auth/model";
import { useMutation } from "@tanstack/react-query";

function useResetPasswordMutation() {
  const {mutate: mutateResetPassword, isPending: mutateResetPasswordPending, isError, error} = useMutation({
    mutationFn: (email: string) => authService.resetPassword(email),
    onSuccess: (data: any) => {
      
      if(data?.success) {
        console.log('data.access', data)
      }
    },
    onError: (error) => {
      console.log('useResetPasswordMutation error', error)
    }
  })

  return {mutateResetPassword, mutateResetPasswordPending, isError, error}

}

export default useResetPasswordMutation;