import Image from "next/image";
import { payTypes } from "@/shared/data/PayMethods";

function PayMethods() {
  return (
    <div className="payMethods">
      <div className="payMethods__items flex items-center gap-3">
        {payTypes.map(pay => (
          <Image key={pay.id} src={pay.icon} alt={pay.label} title={pay.label} width={32} height={55} />
        ))}
      </div>
    </div>
  );
}

export default PayMethods;