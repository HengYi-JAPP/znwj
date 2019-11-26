package com.hengyi.japp.znwj.interfaces.python;

import com.hengyi.japp.znwj.domain.DetectExceptionInfo;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.io.Serializable;
import java.util.Collection;

/**
 * @author jzb 2019-11-21
 */
@Data
@EqualsAndHashCode(onlyExplicitlyIncluded = true)
public class DetectResult implements Serializable {
    @EqualsAndHashCode.Include
    private String code;
    private Collection<DetectExceptionInfo> detectExceptionInfos;
}
