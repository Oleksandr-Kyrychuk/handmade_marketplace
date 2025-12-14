import ConfirmEmailForm from "@/features/confirmEmailForm/ui/confirmEmailForm";

interface IConfirmEmailPage {
  params: 
}

function ConfirmEmailPage({searchParams, params}) {
  console.log('searchParam', searchParams.token)
  console.log('params', params.local)

  const token = searchParams.token
  const locale = params.local

  return (
    <ConfirmEmailForm />
  );
}

export default ConfirmEmailPage;