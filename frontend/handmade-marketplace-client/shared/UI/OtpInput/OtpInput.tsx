import { useRef } from 'react';
import BaseInput from '../Input/BaseInput';
import { IOtpInputProps } from './types/interfaces';

function OtpInput({ maxLength, inputType, inputClassName, isDisabled, isRequired, value, onChange, isHasError }: IOtpInputProps) {
  const inputsRef = useRef<HTMLInputElement[]>([]);

  const handleChange = (index: number) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const char = e.target.value.slice(-1);
    const newChars = value.split('');
    newChars[index] = char;
    onChange?.(newChars.join(""));
    if (char && index < maxLength - 1) {
      inputsRef.current[index + 1]?.focus();
    }
  };

  const handleKeyDown = (index: number) => (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace") {
      e.preventDefault();

      const newChars = value.split("");
      newChars[index] = " ";
      onChange?.(newChars.join(""));
      // if (index > 0) {
      //   inputsRef.current[index - 1]?.focus();
      // }
    }
  };


  const handlePaste = (index: number) => (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "");

    if (!pasted) return;

    // Створюємо новий масив фіксованої довжини
    const newChars = value.split("");
    while (newChars.length < maxLength) newChars.push("");

    let cursor = index; // Починаємо вставляти з поточного індексу

    for (const digit of pasted) {
      if (cursor >= maxLength) break;
      newChars[cursor] = digit;
      cursor++;
    }

    onChange?.(newChars.join(""));

    // Переміщуємо фокус на наступне порожнє поле або на останнє
    if (cursor < maxLength) inputsRef.current[cursor]?.focus();
    else inputsRef.current[maxLength - 1]?.blur();
  };


  return (
    <div className="flex gap-6">
      {Array.from({ length: maxLength }, (_, i) => (
        <BaseInput
          key={i}
          id={`new-${i}`}
          inputType={inputType}
          maxLength={1}
          isDisabled={isDisabled}
          isRequired={isRequired}
          isHasError={isHasError}
          placeholder='-'
          value={value[i] ?? ''}
          onChange={handleChange(i)}
          inputClassName={`${inputClassName} text-center appearance-none [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none [appearance:textfield]`}
          inputRef={(el) => (inputsRef.current[i] = el!)}
          onKeyDown={handleKeyDown(i)}
          onPaste={handlePaste(i)}
        />
      ))}
    </div>
  );
}

export default OtpInput;
