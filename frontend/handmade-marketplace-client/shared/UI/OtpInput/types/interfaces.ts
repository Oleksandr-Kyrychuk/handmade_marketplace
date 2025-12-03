export interface IOtpInput {
  maxLength: number, 
  inputType: string, 
  inputClassName?: string, 
  isDisabled?: boolean, 
  isRequired?: boolean, 
  value: string;
  isHasError?: boolean;
  onChange: (value: string) => void;
}


export type IOtpInputProps = IOtpInput