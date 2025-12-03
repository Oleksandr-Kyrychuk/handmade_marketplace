'use client';

import Link from "next/link";
import AuthLayout from "@/entities/authLayout/ui/AuthLayout";
import { Button } from "@/shared/UI";
import { Path } from "@/shared/enums/Path";
import InputField from "@/shared/UI/Input/InputField";
import { Controller, useForm } from "react-hook-form";
import { LogInRequestDTO } from "../../../entities/auth/model/types/interfaces";
import { yupResolver } from "@hookform/resolvers/yup"
import { logInSchema } from "../validation/validation";
import { useTranslations } from "next-intl";
import PlatformsButtons from "@/entities/platformsButtons/PlatformsButtons";
import { useState } from "react";
import useLogInMutation from "../model/Quries/useLogInMutation";


function LogInForm() {
  const t = useTranslations();

  const [globalError, setGlobalError] = useState('');
  const {mutateLogIn, mutateLoginPending} = useLogInMutation();

  const {handleSubmit, register, formState: {errors}, setError, control} = useForm<LogInRequestDTO>({
    resolver: yupResolver(logInSchema),
  });

  function onSubmit(data: LogInRequestDTO) {
    console.log('data', data)
  }

  return (
    <AuthLayout title="logInPage.title" subtitle="logInPage.subtitle">
      <form autoComplete="false" onSubmit={handleSubmit(onSubmit)} className="lg:mb-12 mb-6">
					<div className="lg:mb-12 mb-6">
						<div className="mb-4">
							<Controller 
								name="email"
								control={control}
								render={({field}) => (
									<InputField 
										{...field}
										id="email"
										inputType="email"
										isHasError={!!errors.email}
										errorText={errors?.email?.message || ''}
										{...register('email')}
										placeholder="Email"
										inputClassName="rounded-5xl font-secondary"
										label={t('form.email')}
									/>
								)}
							/>
						</div>
						<div className="mb-4">
							<div className="flex justify-end">
								<Link href={Path.Reset_Password} className="text-size-link-1 text-primary-600 leading-100 hover:underline duration-500">{t('form.forgot-password')}</Link>
							</div>
							<div className="relative">
								<Controller 
								name="password"
								control={control}
								render={({field}) => (
									<InputField
										{...field}
										id="password"
										inputType="password"
										{...register('password')}
										inputClassName="rounded-5xl font-secondary pr-12"
										placeholder={t('form.enter-password')}
										isHasError={!!errors.password}
										errorText={errors?.password?.message || ''}
										label={t('form.password')}
									/>
								)}
							/>	
							</div>
						</div>
					</div>


					{globalError && (
						<p style={{ color: "red" }} className="mb-4">
							{globalError}
						</p>
					)}

					<Button
						type="submit"
						className="w-full font-bold leading-100 text-size-body-2 h-14"
						size="md"
						variant="default"
						disabled={mutateLoginPending}
					>
						{t('form.login')}
					</Button>
				</form>

				<div className="separateBlock relative text-center mb-6">
					<span className="bg-transparent relative z-10 px-2 text-primary-400 separateBlock__text leading-130 inline-block">
						{t('form.or-log-in-with')}
					</span>
				</div>

					<PlatformsButtons />
				

				<div className="formBottom">
					<div className="flex justify-center items-center lg:flex-row flex-col ">
						<div className="text-size-body-3 leading-130 lg:mb-0 mb-2 font-secondary">
							{t('form.without-registration')}
							
						</div>
						<Link href={Path.Registration}
							className="text-primary-600 text-size-link-1 ml-2 leading-100"
						>
							{t('form.registration')}
						</Link>
					</div>
				</div>
    </AuthLayout>
  );
}

export default LogInForm;