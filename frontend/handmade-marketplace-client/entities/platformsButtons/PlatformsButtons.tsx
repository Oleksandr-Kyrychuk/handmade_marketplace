import { FacebookIcon, GoogleIcon, PinterestIcon } from "@/assets/Icons";
import { Button } from "@/shared/UI";



function PlatformsButtons() {
  return (
    <>
      <div className="flex justify-center gap-4 mb-12">
          <Button type="button" className="flex items-center hover:opacity-35 duration-500 w-[56px] h-[56px] !p-0" variant="secondary">
            <FacebookIcon className='text-snow w-6'/>
          </Button>
          <Button type="button" className="flex items-center hover:opacity-35 duration-500 w-[56px] h-[56px] !p-0" variant="secondary">
            <PinterestIcon className='text-snow w-6' />
          </Button>
          <Button type="button" className="flex items-center hover:opacity-35 duration-500 w-[56px] h-[56px] !p-0" variant="secondary">
            <GoogleIcon className='text-snow w-6' />
          </Button>
      </div>
    </>
  );
}

export default PlatformsButtons;