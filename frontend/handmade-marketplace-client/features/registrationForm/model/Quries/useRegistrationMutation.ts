import { authService } from "@/entities/auth/model";
import { SignUpRequestDTO } from "@/entities/auth/model/types/interfaces";
import { useMutation } from "@tanstack/react-query";

function useRegistrationMutation() {
  const {mutate: registrationMutation, isPending: registrationPending, isError, error} = useMutation({
    mutationFn: (data: SignUpRequestDTO) => authService.signUpAuth(data),
    onSuccess: () => {
      console.log('useSignUpMutation work');
    },
    onError: (error) => {
      console.log('useSignUpMutation error: ', error)
    },
  })

  return {registrationMutation, registrationPending, isError, error}
}

export default useRegistrationMutation;